from fastapi import FastAPI
from fastapi.responses import JSONResponse
from routes.api_v1 import router as v1_router
from utils.logger import LoggerSetup
import uvicorn
import logging

# Setup logging
logger = LoggerSetup.setup()
app_logger = logging.getLogger("codeerax_heart.main")

app = FastAPI(
    title="Codeerax Heart API",
    version="1.0.0",
    description="Brain -> Heart -> Execute -> Response"
)

# Include routes
app.include_router(v1_router, prefix="/api/v1")

@app.get("/")
def health_check():
    app_logger.info("Health check request")
    return {
        "status": "Heart is beating",
        "service": "codeerax_heart",
        "version": "1.0.0"
    }

@app.get("/health/detailed")
def detailed_health():
    """Get detailed health status"""
    return {
        "status": "operational",
        "service": "codeerax_heart",
        "components": {
            "engine": "running",
            "state_registry": "active",
            "workflow_queue": "ready"
        }
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    app_logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    app_logger.info("Starting Codeerax Heart API...")
    uvicorn.run(app, host="127.0.0.1", port=8000)