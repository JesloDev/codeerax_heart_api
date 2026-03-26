from typing import Dict, Any, Optional
from pydantic import BaseModel

class TaskRequest(BaseModel):
    action_type: str
    payload: Dict[str, Any]
    priority: int = 1
    
class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str