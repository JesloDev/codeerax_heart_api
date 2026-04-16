from typing import Dict, Any, Optional
import logging
from datetime import datetime

from schemas.execution import TaskRequest, TaskResponse
from runtime.state import StateRegistry, TaskStatus
from services.runner import WorkflowQueue
from services.actions import ActionValidator


class ExecutionController:
    """Handles execution requests from the Brain API"""
    
    def __init__(self, state_registry: StateRegistry, workflow_queue: WorkflowQueue):
        self.state_registry = state_registry
        self.workflow_queue = workflow_queue
        self.logger = logging.getLogger(__name__)
    
    async def execute_task(self, request: TaskRequest) -> TaskResponse:
        """
        Process an execution request from the Brain.
        
        Steps:
        1. Validate request
        2. Create task in state registry
        3. Enqueue for execution
        4. Return task ID and status
        """
        self.logger.info(f"Received execution request for action: {request.action_type}")
        
        try:
            # Step 1: Validate
            is_valid, error_msg = ActionValidator.validate_action(
                request.action_type, 
                request.payload
            )
            
            if not is_valid:
                self.logger.warning(f"Invalid request: {error_msg}")
                raise ValueError(error_msg)
            
            # Step 2: Create task
            task = self.state_registry.create_task(
                action_type=request.action_type,
                payload=request.payload,
                priority=request.priority
            )
            
            self.logger.info(f"Task created: {task.task_id}")
            
            # Step 3: Enqueue
            await self.workflow_queue.enqueue_and_execute(task)
            
            # Step 4: Return response
            return TaskResponse(
                task_id=task.task_id,
                status="accepted",
                message=f"Action {request.action_type} is now beating."
            )
        
        except ValueError as e:
            self.logger.error(f"Validation error: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Execution error: {str(e)}")
            raise
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get the status of a task"""
        task = self.state_registry.get_task(task_id)
        
        if not task:
            self.logger.warning(f"Task {task_id} not found")
            return {
                "task_id": task_id,
                "status": "NOT_FOUND",
                "message": f"Task {task_id} does not exist"
            }
        
        self.logger.info(f"Status check for task {task_id}: {task.status.value}")
        
        return {
            "task_id": task_id,
            "status": task.status.value,
            "action_type": task.action_type,
            "priority": task.priority,
            "created_at": task.created_at.isoformat(),
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "result": task.result,
            "error": task.error
        }
    
    def get_all_tasks(self, status: Optional[str] = None) -> Dict[str, Any]:
        """Get all tasks, optionally filtered by status"""
        if status:
            try:
                task_status = TaskStatus[status.upper()]
                tasks = self.state_registry.get_tasks_by_status(task_status)
            except KeyError:
                self.logger.warning(f"Invalid status filter: {status}")
                return {
                    "error": f"Invalid status: {status}",
                    "valid_statuses": [s.value for s in TaskStatus]
                }
        else:
            tasks = self.state_registry.get_all_tasks()
        
        return {
            "total_count": len(tasks),
            "tasks": [task.to_dict() for task in tasks.values()]
        }
    
    def get_active_tasks_count(self) -> int:
        """Get count of currently active (running) tasks"""
        pending = self.state_registry.get_tasks_by_status(TaskStatus.PENDING)
        running = self.state_registry.get_tasks_by_status(TaskStatus.RUNNING)
        return len(pending) + len(running)
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Get workflow queue statistics"""
        all_tasks = self.state_registry.get_all_tasks()
        
        stats = {
            "total_tasks": len(all_tasks),
            "active_tasks": self.workflow_queue.get_active_task_count(),
            "by_status": {}
        }
        
        for status in TaskStatus:
            count = len(self.state_registry.get_tasks_by_status(status))
            stats["by_status"][status.value] = count
        
        return stats
