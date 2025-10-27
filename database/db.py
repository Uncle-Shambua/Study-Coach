from sqlmodel import create_engine, SQLModel
from sqlmodel import  Session as sesh
from fastapi import Depends
from typing import Annotated
from models.models import  Session, QuestionDb, Interrogation

engine = create_engine("sqlite:///database.db", echo=True)

def create_everything():
    SQLModel.metadata.create_all(engine)

def session_factory():
    with sesh(engine) as session:
        yield session


session_dependency = Annotated[sesh, Depends(session_factory)]