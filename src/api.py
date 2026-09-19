from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from src.concurrency.orchestrator import answer_question

import mimetypes

# .jsx uzantısını düzgün JavaScript MIME tipi kimi tanıdırıq
mimetypes.add_type("application/javascript", ".jsx")
mimetypes.add_type("text/javascript", ".js")

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

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Frontend üçün search endpointi (artıq mənbələri də qaytarır)
@app.post("/api/search")
async def search_endpoint(request: SearchRequest):
    try:
        result = await answer_question(request.query)
        answer_text = result.get("answer", "") if isinstance(result, dict) else str(result)
        sources_list = result.get("sources", []) if isinstance(result, dict) else []
        
        return {
            "status": "success",
            "query": request.query,
            "answer": answer_text,
            "sources": sources_list
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

# Komanda yoldaşının əlavə etdiyi ask endpointi (artıq mənbələri də qaytarır)
@app.post("/ask")
async def ask_endpoint(request: AskRequest):
    """Run the research assistant pipeline for a given query."""
    result = await answer_question(query=request.query, sources_str=request.sources)
    answer_text = result.get("answer", "") if isinstance(result, dict) else str(result)
    sources_list = result.get("sources", []) if isinstance(result, dict) else []
    
    return {
        "query": request.query,
        "answer": answer_text,
        "sources": sources_list
    }

# Frontend interfeysini birbaşa əsas səhifəyə (/) bağlayırıq
# (Diqqət: Bütün API endpoint-ləri işləməsi üçün bu mount həmişə ən sonda olmalıdır)
app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="frontend")