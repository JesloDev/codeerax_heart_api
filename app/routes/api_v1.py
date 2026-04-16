from fastapi import APIRouter, Depends, HTTPException
from schemas.execution import TaskRequest, TaskResponse
from runtime.engine import HeartEngine
from internal_api.security import validate_brain_request
import logging

router = APIRouter()
engine = HeartEngine()
logger = logging.getLogger(__name__)

# Initialize engine for all routes
@router.on_event("startup")
async def startup_event():
    logger.info("API v1 routes initialized")

# ============================================================================
# EXECUTION ENDPOINTS
# ============================================================================

@router.post("/execute", response_model=TaskResponse, dependencies=[Depends(validate_brain_request)])
async def trigger_execution(req: TaskRequest):
    """
    Trigger task execution from Brain API.
    
    Protected endpoint - requires X-Heart-Signature header.
    
    Workflow:
    1. Validate request and security
    2. Create task in registry
    3. Queue for execution
    4. Return task ID
    """
    try:
        logger.info(f"Execution request: {req.action_type}")
        
        # Use controller to handle request
        response = await engine.controller.execute_task(req)
        
        return response
    
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Execution error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ============================================================================
# STATUS ENDPOINTS
# ============================================================================

@router.get("/status/{task_id}")
async def get_status(task_id: str):
    """Get the status of a task (public endpoint)"""
    logger.info(f"Status request for task: {task_id}")
    
    try:
        return engine.controller.get_task_status(task_id)
    except Exception as e:
        logger.error(f"Status check error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/tasks")
async def list_all_tasks(status: str = None):
    """List all tasks, optionally filtered by status"""
    logger.info(f"List tasks request with status filter: {status}")
    
    try:
        return engine.controller.get_all_tasks(status)
    except Exception as e:
        logger.error(f"List tasks error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ============================================================================
# STATS ENDPOINTS
# ============================================================================

@router.get("/stats")
async def get_stats():
    """Get execution statistics"""
    logger.info("Stats request")
    
    try:
        return engine.get_stats()
    except Exception as e:
        logger.error(f"Stats error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/active-tasks")
async def get_active_tasks_count():
    """Get count of active tasks"""
    try:
        count = engine.controller.get_active_tasks_count()
        return {"active_tasks": count}
    except Exception as e:
        logger.error(f"Active tasks count error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ============================================================================
# INFO ENDPOINTS
# ============================================================================

@router.get("/actions")
async def list_available_actions():
    """List available action types"""
    from services.actions import ActionFactory
    
    actions = ActionFactory.get_available_actions()
    return {
        "available_actions": actions,
        "count": len(actions)
    }