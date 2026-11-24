from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

from .answer import ask

app = FastAPI(title="repoqa")


class Q(BaseModel):
    question: str


@app.post("/api/ask")
def api_ask(q: Q):
    return ask(q.question)


@app.get("/")
def index():
    return FileResponse("static/index.html")
