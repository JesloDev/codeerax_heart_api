from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
import uuid


class TaskStatus(str, Enum):
    """Task execution status"""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


@dataclass
class TaskState:
    """Represents the state of a single task execution"""
    task_id: str
    action_type: str
    payload: Dict[str, Any]
    status: TaskStatus = TaskStatus.PENDING
    priority: int = 1
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task state to dictionary"""
        return {
            "task_id": self.task_id,
            "action_type": self.action_type,
            "status": self.status.value,
            "priority": self.priority,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "result": self.result,
            "error": self.error
        }


class StateRegistry:
    """Manages task state storage and retrieval"""
    
    def __init__(self):
        self.store: Dict[str, TaskState] = {}
    
    def create_task(self, action_type: str, payload: Dict[str, Any], priority: int = 1) -> TaskState:
        """Create a new task state"""
        task_id = str(uuid.uuid4())
        task = TaskState(
            task_id=task_id,
            action_type=action_type,
            payload=payload,
            priority=priority
        )
        self.store[task_id] = task
        return task
    
    def get_task(self, task_id: str) -> Optional[TaskState]:
        """Retrieve a task by ID"""
        return self.store.get(task_id)
    
    def update_status(self, task_id: str, status: TaskStatus, error: Optional[str] = None) -> bool:
        """Update task status"""
        task = self.get_task(task_id)
        if not task:
            return False
        
        task.status = status
        
        if status == TaskStatus.RUNNING and not task.started_at:
            task.started_at = datetime.utcnow()
        elif status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
            task.completed_at = datetime.utcnow()
        
        if error:
            task.error = error
        
        return True
    
    def set_result(self, task_id: str, result: Dict[str, Any]) -> bool:
        """Set task result"""
        task = self.get_task(task_id)
        if not task:
            return False
        task.result = result
        return True
    
    def get_all_tasks(self) -> Dict[str, TaskState]:
        """Get all tasks"""
        return self.store.copy()
    
    def get_tasks_by_status(self, status: TaskStatus) -> Dict[str, TaskState]:
        """Get all tasks with a specific status"""
        return {
            task_id: task 
            for task_id, task in self.store.items() 
            if task.status == status
        }
