from pydantic_ai import Agent, PromptedOutput
from dotenv import load_dotenv
from models.models import Question
load_dotenv()

MODEL= "google-gla:gemini-2.0-flash"
question_agent = Agent(
    model=MODEL,
    system_prompt= """
        You are a study Companion, You are expected to come up with questions based on the study material that the user provide:
        The question should contain:
        - The question 
        - Multiple Choices
        -The correct answer
        - The explanation as to why that is the correct answer
    """,
    output_type=PromptedOutput(list[Question])
)

question_chat_agent = Agent(
    model = MODEL,
    system_prompt= """
        You are a study companion, You help the user understand the questions and the picked answer based on the learning document provided
        Your answers should be based on the information found in the learning document provided,
    """
)