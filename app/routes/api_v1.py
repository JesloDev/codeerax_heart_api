from fastapi import APIRouter, Depends, HTTPException
from app.schemas.execution import TaskRequest, TaskResponse
from app.runtime.engine import HeartEngine
from app.internal_api.security import validate_brain_request

router = APIRouter()
engine = HeartEngine()

# This endpoint is protected
@router.post("/execute", response_model=TaskResponse, dependencies=[Depends(validate_brain_request)])
async def trigger_execution(req: TaskRequest):
    tid = await engine.pulse(req.action_type, req.payload)
    return {
        "task_id": tid,
        "status": "accepted",
        "message": f"Action {req.action_type} is now beating."
    }

# This route is let public
@router.get("/status/{task_id}")
async def get_status(task_id: str):
    status = engine.registry.get(task_id, "NOT_FOUND")
    return {"task_id": task_id, "status": status}