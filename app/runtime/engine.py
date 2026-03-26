import uuid
import asyncio

class HeartEngine:
    def __init__(self):
        self.registry = {} # TaskID -> Status
        
    async def pulse(self, action_type: str, data: dict):
        task_id = str(uuid.uuid4())
        self.registry[task_id] = "PENDING"
        
        asyncio.create_task(self.execute_work(task_id, action_type, data))
        
        return task_id
    
    async def execute_work(self, tid: str, action: str, data: dict):
            self.registry[tid] = "RUNNING"
            try:
                # Simulate work (services/actions.py is called here)
                await asyncio.sleep(2)
                self.registry[tid] = "COMPLETED"
            except Exception:
                self.registry[tid] = "FAILED"