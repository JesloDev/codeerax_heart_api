from typing import Dict, Any, Callable, Optional
from abc import ABC, abstractmethod
import asyncio
from datetime import datetime


class Action(ABC):
    """Base class for all actions"""
    
    @abstractmethod
    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the action"""
        pass
    
    @abstractmethod
    def validate(self, payload: Dict[str, Any]) -> bool:
        """Validate payload for this action"""
        pass


class DataProcessingAction(Action):
    """Action for data processing tasks"""
    
    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process data synchronously or asynchronously"""
        data = payload.get("data", [])
        operation = payload.get("operation", "sum")
        
        await asyncio.sleep(0.5)  # Simulate processing
        
        if operation == "sum":
            result = sum(data) if isinstance(data, list) else 0
        elif operation == "count":
            result = len(data) if isinstance(data, list) else 0
        elif operation == "average":
            result = sum(data) / len(data) if isinstance(data, list) and len(data) > 0 else 0
        else:
            result = None
        
        return {
            "operation": operation,
            "result": result,
            "processed_at": datetime.utcnow().isoformat(),
            "data_count": len(data) if isinstance(data, list) else 0
        }
    
    def validate(self, payload: Dict[str, Any]) -> bool:
        """Validate data processing payload"""
        return "data" in payload and isinstance(payload.get("data"), list)


class EventNotificationAction(Action):
    """Action for sending event notifications"""
    
    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Send notification"""
        event_type = payload.get("event_type", "generic")
        message = payload.get("message", "")
        recipients = payload.get("recipients", [])
        
        await asyncio.sleep(0.3)  # Simulate sending
        
        return {
            "event_type": event_type,
            "message": message,
            "recipients_count": len(recipients),
            "sent_at": datetime.utcnow().isoformat(),
            "status": "sent"
        }
    
    def validate(self, payload: Dict[str, Any]) -> bool:
        """Validate notification payload"""
        return "message" in payload and "recipients" in payload


class LocationTrackingAction(Action):
    """Action for location tracking"""
    
    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Track location data"""
        latitude = payload.get("latitude")
        longitude = payload.get("longitude")
        user_id = payload.get("user_id")
        
        await asyncio.sleep(0.4)  # Simulate tracking
        
        return {
            "user_id": user_id,
            "location": {
                "latitude": latitude,
                "longitude": longitude
            },
            "tracked_at": datetime.utcnow().isoformat(),
            "status": "tracked"
        }
    
    def validate(self, payload: Dict[str, Any]) -> bool:
        """Validate location payload"""
        return all(k in payload for k in ["latitude", "longitude", "user_id"])


class ActionFactory:
    """Factory for creating action instances"""
    
    _actions: Dict[str, type] = {
        "data_processing": DataProcessingAction,
        "event_notification": EventNotificationAction,
        "location_tracking": LocationTrackingAction,
    }
    
    @classmethod
    def register_action(cls, name: str, action_class: type) -> None:
        """Register a new action type"""
        if not issubclass(action_class, Action):
            raise ValueError(f"{action_class} must inherit from Action")
        cls._actions[name] = action_class
    
    @classmethod
    def create_action(cls, action_type: str) -> Optional[Action]:
        """Create an action instance by type"""
        action_class = cls._actions.get(action_type)
        if action_class:
            return action_class()
        return None
    
    @classmethod
    def get_available_actions(cls) -> Dict[str, str]:
        """Get all available action types"""
        return list(cls._actions.keys())


class ActionValidator:
    """Validates actions before execution"""
    
    @staticmethod
    def validate_action(action_type: str, payload: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate an action and payload"""
        action = ActionFactory.create_action(action_type)
        
        if not action:
            return False, f"Unknown action type: {action_type}"
        
        if not action.validate(payload):
            return False, f"Invalid payload for action: {action_type}"
        
        return True, None
