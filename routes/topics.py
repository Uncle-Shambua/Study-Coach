from botocore.compat import file_type
from fastapi import APIRouter, UploadFile, WebSocket, WebSocketDisconnect, WebSocketException, HTTPException
from fastapi.responses import JSONResponse
from services.agents import question_agent, question_chat_agent
from pydantic_ai import BinaryContent
from pydantic_ai.messages import ModelMessagesTypeAdapter
from database.db import session_dependency
from models.models import QuestionDb, Session, Interrogation
from sqlmodel import  select


topics_router = APIRouter(prefix="/topic")

@topics_router.post("/get-questions/")
async def get_questions(file: UploadFile, questions: int, session: session_dependency):
    file_data = await file.read()
    response = await question_agent.run(
        [
            BinaryContent(file_data, media_type=file.content_type),
            f"generate {questions} questions"
        ]
    )

    db_session = Session(
        session_name= file.filename,
        file = file_data,
        file_type = file.content_type,
        questions= [
            QuestionDb(

                question= question.question,
                choices = "->".join(question.choices),
                correct_answer = question.correct_answer,
                explanation = question.explanation
            ) for question in response.output
        ]
    )
    session.add(db_session)
    session.commit()
    session.refresh(db_session)
    return JSONResponse(
        {
            "file_name": db_session.session_name,
            "id": db_session.id,
            "questions":[
                {
                    "id": question.id,
                    "question": question.question,
                    "choices": question.choices_list,
                    "correct_answer": question.correct_answer,
                    "explanation": question.explanation
                } for question in db_session.questions
            ]
        },
        status_code=201
    )

def fetch_history(id: int, session: session_dependency):
    message =  session.exec(select(Interrogation).where(Interrogation.question_id == id)).first()
    if message:
        return ModelMessagesTypeAdapter.validate_json(
           message.message_history
        )
    else:
        return None
def add_message(question_id: int, message, session: session_dependency):
    existing = session.exec(select(Interrogation).where(Interrogation.id == question_id)).first()
    if existing:
        existing.message_history = message
    else:
        existing = Interrogation(
            question_id= question_id,
            message_history= message
        )
        session.add(existing)

    session.commit()
    print("Commitment done no Issues")

@topics_router.websocket("/ws/question-the-question/")
async def question_the_question_socket(question_id: int, websocket: WebSocket, session: session_dependency):
    question = session.exec(select(QuestionDb).where(QuestionDb.id == question_id)).first()
    if not question:
        raise HTTPException(
            status_code=404,
            detail="The question does not exist"
        )
    try:
        await  websocket.accept()
        while True:
            request = await  websocket.receive_json()
            response = await question_chat_agent.run(
                [
                    BinaryContent(data=question.session.file, media_type=question.session.file_type),
                    f"The Question was {question.question} and the answer was {question.correct_answer} from {question.choices}",
                    f"The user says: {request["prompt"]}"
                ]if bool(request["first"]) else request["prompt"],
                message_history=fetch_history(question_id, session=session)
            )

            await  websocket.send_text(response.output)
            add_message(question_id=question_id, message=response.all_messages_json(), session=session)
    except WebSocketDisconnect:
        print("User Disconnected")








