from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.concurrency.orchestrator import answer_question

app = FastAPI(title="Research Assistant API")

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchRequest(BaseModel):
    query: str

class AskRequest(BaseModel):
    query: str
    sources: str = "wikipedia,arxiv,web"

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Research Assistant API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Frontend üçün search endpointi
@app.post("/api/search")
async def search_endpoint(request: SearchRequest):
    try:
        result_answer = await answer_question(request.query)
        return {
            "status": "success",
            "query": request.query,
            "answer": result_answer
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

# Komanda yoldaşının əlavə etdiyi ask endpointi
@app.post("/ask")
async def ask_endpoint(request: AskRequest):
    """Run the research assistant pipeline for a given query."""
    answer = await answer_question(query=request.query, sources_str=request.sources)
    return {"query": request.query, "answer": answer}