from fastapi import FastAPI
from routes.api_v1 import router as v1_router

app = FASTAPI(title="Codeerax Heart API", version="1.0.0")

app.include_router(v1_router, prefix="/api/v1")

@app.get("/")
def health_check():
    return {"status": "Heart is beating", "service": "codeerax_heart"}