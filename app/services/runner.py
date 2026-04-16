from typing import Dict, Any, Optional
import asyncio
import logging
from datetime import datetime

from services.actions import ActionFactory, ActionValidator
from runtime.state import TaskState, TaskStatus, StateRegistry


class WorkflowRunner:
    """Orchestrates task execution workflow"""
    
    def __init__(self, state_registry: StateRegistry):
        self.state_registry = state_registry
        self.logger = logging.getLogger(__name__)
    
    async def run(self, task: TaskState) -> Dict[str, Any]:
        """
        Execute a complete workflow for a task.
        
        Workflow:
        1. Validate action and payload
        2. Update status to RUNNING
        3. Execute action
        4. Handle result/error
        5. Update task state
        """
        try:
            # Step 1: Validate
            is_valid, error_msg = ActionValidator.validate_action(task.action_type, task.payload)
            if not is_valid:
                await self._handle_failure(task.task_id, error_msg)
                return {"success": False, "error": error_msg}
            
            # Step 2: Update to RUNNING
            self.state_registry.update_status(task.task_id, TaskStatus.RUNNING)
            self.logger.info(f"Task {task.task_id} started execution")
            
            # Step 3: Execute action
            action = ActionFactory.create_action(task.action_type)
            result = await action.execute(task.payload)
            
            # Step 4: Handle result
            self.state_registry.set_result(task.task_id, result)
            self.state_registry.update_status(task.task_id, TaskStatus.COMPLETED)
            
            self.logger.info(f"Task {task.task_id} completed successfully")
            
            return {
                "success": True,
                "task_id": task.task_id,
                "result": result
            }
        
        except asyncio.TimeoutError:
            await self._handle_failure(task.task_id, "Task execution timeout")
            return {"success": False, "error": "Task execution timeout"}
        
        except Exception as e:
            error_msg = str(e)
            await self._handle_failure(task.task_id, error_msg)
            self.logger.error(f"Task {task.task_id} failed: {error_msg}")
            return {"success": False, "error": error_msg}
    
    async def _handle_failure(self, task_id: str, error: str) -> None:
        """Handle task failure"""
        self.state_registry.update_status(task_id, TaskStatus.FAILED, error=error)
        self.logger.error(f"Task {task_id} failed: {error}")


class WorkflowQueue:
    """Manages task queue and execution"""
    
    def __init__(self, state_registry: StateRegistry, max_workers: int = 5):
        self.state_registry = state_registry
        self.runner = WorkflowRunner(state_registry)
        self.max_workers = max_workers
        self.active_tasks = set()
        self.logger = logging.getLogger(__name__)
    
    async def enqueue_and_execute(self, task: TaskState) -> str:
        """Enqueue a task and execute it"""
        self.logger.info(f"Task {task.task_id} enqueued")
        
        # Execute immediately in this implementation
        # In production, you might want to use a real queue system
        asyncio.create_task(self._execute_task(task))
        
        return task.task_id
    
    async def _execute_task(self, task: TaskState) -> None:
        """Execute a task with concurrency control"""
        while len(self.active_tasks) >= self.max_workers:
            await asyncio.sleep(0.1)
        
        self.active_tasks.add(task.task_id)
        try:
            await self.runner.run(task)
        finally:
            self.active_tasks.discard(task.task_id)
    
    def get_active_task_count(self) -> int:
        """Get number of currently active tasks"""
        return len(self.active_tasks)
    
    async def wait_for_task(self, task_id: str, timeout: int = 30) -> Optional[TaskState]:
        """Wait for a specific task to complete"""
        start_time = asyncio.get_event_loop().time()
        
        while asyncio.get_event_loop().time() - start_time < timeout:
            task = self.state_registry.get_task(task_id)
            if task and task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                return task
            
            await asyncio.sleep(0.5)
        
        self.logger.warning(f"Task {task_id} did not complete within {timeout} seconds")
        return None
