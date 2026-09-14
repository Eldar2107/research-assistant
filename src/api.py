from fastapi import FastAPI

app = FastAPI(title="Research Assistant API")


@app.get("/")
def read_root():
  return {"status": "ok", "message": "Research Assistant API is running"}


@app.get("/health")
def health_check():
  return {"status": "healthy"}