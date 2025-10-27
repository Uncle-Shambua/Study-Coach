from fastapi import FastAPI
from contextlib import asynccontextmanager
from database.db import  create_everything
from routes.topics import topics_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_everything()
    yield
    print("Shutting down")
server = FastAPI(lifespan=lifespan)

server.include_router(topics_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app="main:server", reload=True)

