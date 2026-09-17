from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.concurrency.orchestrator import answer_question

app = FastAPI(title="Research Assistant API")

# CORS ayarları (Frontend-in sorğunu qəbul etməsi üçün)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchRequest(BaseModel):
    query: str

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Research Assistant API is running"}

@app.post("/api/search")
async def search_endpoint(request: SearchRequest):
    try:
        # Orkestratoru işə salırıq və həqiqi süni intellekt cavabını gözləyirik
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