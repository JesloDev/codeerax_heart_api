import uuid
import asyncio
from datetime import datetime
import logging

from runtime.state import StateRegistry, TaskStatus
from services.runner import WorkflowQueue
from controllers.exec_controller import ExecutionController
from logs.tracker import get_execution_logger


class HeartEngine:
    """
    Core execution engine for the Heart API.
    
    Responsibilities:
    - Maintain task registry
    - Orchestrate workflow execution
    - Coordinate with runner and logger
    
    Workflow: Brain -> HeartEngine -> ExecutionController -> WorkflowRunner -> Action
    """
    
    def __init__(self):
        self.state_registry = StateRegistry()
        self.workflow_queue = WorkflowQueue(self.state_registry, max_workers=5)
        self.controller = ExecutionController(self.state_registry, self.workflow_queue)
        self.execution_logger = get_execution_logger()
        self.logger = logging.getLogger(__name__)
        
        # Legacy compatibility
        self.registry = {}  # TaskID -> Status (deprecated, use state_registry instead)
    
    async def pulse(self, action_type: str, data: dict, priority: int = 1) -> str:
        """
        Trigger a task execution through the Heart Engine.
        
        Args:
            action_type: Type of action to execute
            data: Payload for the action
            priority: Task priority (default: 1)
        
        Returns:
            Task ID for tracking
        """
        task_id = str(uuid.uuid4())
        
        # Create task in state registry
        task = self.state_registry.create_task(
            action_type=action_type,
            payload=data,
            priority=priority
        )
        
        # For legacy compatibility
        self.registry[task_id] = "PENDING"
        
        self.logger.info(f"Heart pulse: {action_type} (task_id: {task.task_id})")
        self.execution_logger.log_task_start(task.task_id, action_type, data)
        
        # Enqueue for execution
        asyncio.create_task(self.execute_work(task.task_id, action_type, data))
        
        return task.task_id
    
    async def execute_work(self, task_id: str, action_type: str, data: dict) -> None:
        """
        Execute workflow for a task.
        
        Workflow Steps:
        1. Update status to RUNNING
        2. Execute action through runner
        3. Handle completion or failure
        4. Log results
        """
        start_time = datetime.utcnow()
        
        try:
            self.registry[task_id] = "RUNNING"
            self.state_registry.update_status(task_id, TaskStatus.RUNNING)
            
            self.logger.info(f"Executing task: {task_id}")
            
            # Execute through workflow runner
            task = self.state_registry.get_task(task_id)
            result = await self.workflow_queue.runner.run(task)
            
            if result.get("success"):
                self.registry[task_id] = "COMPLETED"
                duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
                self.execution_logger.log_task_completed(
                    task_id, 
                    action_type, 
                    result.get("result", {}),
                    duration_ms
                )
                self.logger.info(f"Task completed: {task_id}")
            else:
                self.registry[task_id] = "FAILED"
                duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
                self.execution_logger.log_task_failed(
                    task_id,
                    action_type,
                    result.get("error", "Unknown error"),
                    duration_ms
                )
                self.logger.error(f"Task failed: {task_id} - {result.get('error')}")
        
        except Exception as e:
            self.registry[task_id] = "FAILED"
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            self.execution_logger.log_task_failed(
                task_id,
                action_type,
                str(e),
                duration_ms
            )
            self.logger.error(f"Task execution error: {task_id} - {str(e)}")
    
    def get_status(self, task_id: str) -> str:
        """Get task status (legacy compatibility)"""
        return self.registry.get(task_id, "NOT_FOUND")
    
    def get_task_details(self, task_id: str) -> dict:
        """Get detailed task information"""
        task = self.state_registry.get_task(task_id)
        if not task:
            return {"error": "Task not found"}
        return task.to_dict()
    
    def get_stats(self) -> dict:
        """Get engine statistics"""
        return self.controller.get_queue_stats()