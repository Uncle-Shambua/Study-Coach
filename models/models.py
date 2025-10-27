from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional

class Question(BaseModel):
    question: str
    choices: list[str]
    correct_answer: str
    explanation: str


class Session(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_name: str
    file: bytes
    file_type: str
    questions: Optional[list["QuestionDb"]] = Relationship(back_populates="session")

class QuestionDb(SQLModel, table=True):
    id: int | None = Field(primary_key=True)
    question: str = Field(index=True)
    choices: str
    correct_answer :str
    explanation: str
    session_id: Optional[int] = Field(default=None, foreign_key="session.id")
    session: Optional[Session] = Relationship(back_populates="questions")
    interrogation: Optional["Interrogation"] = Relationship(back_populates="question")

    @property
    def choices_list(self) -> list[str]:
        return self.choices.split("->")

class Interrogation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    question_id: Optional[int] = Field(default=None, foreign_key="questiondb.id")
    question: Optional[QuestionDb] = Relationship(back_populates="interrogation")
    message_history: str
