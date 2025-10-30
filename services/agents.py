from pydantic_ai import Agent, PromptedOutput
from dotenv import load_dotenv
from models.models import Question
from requests import get
from bs4 import BeautifulSoup

load_dotenv()

MODEL = "google-gla:gemini-2.0-flash"
question_agent = Agent(
    model=MODEL,
    system_prompt="""
        You are a study Companion, You are expected to come up with questions based on the study material that the user provide:
        When the user provides a url use the 'generate_notes' tool to generate the notes from which the questions are to be generated
        The question should contain:
        - The question 
        - Multiple Choices
        -The correct answer
        - The explanation as to why that is the correct answer
    """,
    output_type=PromptedOutput(list[Question]),
)


@question_agent.tool_plain
def generate_notes(url: str) -> str:
    """A tool that takes a url and returns the text contained in the url

    Args:
        url (str): The url provided by the user

    Returns:
        str: Either a message showing that the url is not working or the text from the url
    """
    try:
        response = get(url)
    except:
        return f"Error: You might wanna try again"
    if not response.ok:
        return "The Url does not work"

    body = BeautifulSoup(response.text, "html.parser").body
    for script in body:
        script.decompose()
    return body


question_chat_agent = Agent(
    model=MODEL,
    system_prompt="""
        You are a study companion, You help the user understand the questions and the picked answer based on the learning document provided
        Your answers should be based on the information found in the learning document provided,
    """,
)
