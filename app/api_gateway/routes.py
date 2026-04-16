from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class SimpleTaskRequest(BaseModel):
    """Simplified task request for public API"""
    action_type: str
    payload: Dict[str, Any]


@router.post("/submit-task")
async def submit_task_simple(request: SimpleTaskRequest):
    """
    Simplified task submission endpoint for the public API gateway.
    
    This is an optional public-facing endpoint that can submit tasks
    to the Heart API without requiring authentication.
    """
    logger.info(f"Public task submission: {request.action_type}")
    
    return {
        "message": "Task submitted successfully",
        "action_type": request.action_type,
        "note": "Please use the protected /api/v1/execute endpoint with proper authentication"
    }


@router.get("/info")
async def gateway_info():
    """Get information about the API Gateway"""
    return {
        "gateway": "Codeerax Heart API Gateway",
        "version": "1.0.0",
        "endpoints": {
            "protected": "/api/v1/execute (requires X-Heart-Signature header)",
            "public": "/api/v1/status/{task_id}",
            "admin": "/api/v1/stats"
        }
    }
