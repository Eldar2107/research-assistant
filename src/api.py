from fastapi import FastAPI
from pydantic import BaseModel
from src.concurrency.orchestrator import answer_question

app = FastAPI(title="Research Assistant API")


class AskRequest(BaseModel):
    query: str
    sources: str = "wikipedia,arxiv,web"


@app.get("/")
def read_root():
  return {"status": "ok", "message": "Research Assistant API is running"}


@app.get("/health")
def health_check():
  return {"status": "healthy"}


@app.post("/ask")
async def ask_endpoint(request: AskRequest):
  """Run the research assistant pipeline for a given query."""
  answer = await answer_question(query=request.query, sources_str=request.sources)
  return {"query": request.query, "answer": answer}