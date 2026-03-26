Codeerax Heart API
The execution engine for the Codeerax Ecosystem

Prerequisites:
    Python 3.10+
    Virtual environment (venv)

Installation:
    1. Clone repository
    2. Create and activate your virtual environment
    3. Install dependencies:
            pip install -r requirements.txt

Heart API - Execution Engine
Base URL: http://localhost:8000/api/v1

Security and Authentication:
    Header Name: X-Heart-Signature
    Value: super_secure_random_string





API Endpoints
1. [POST] /api/v1/execute
    Triggers a new execution workflow. (Protected)
    
    Payload Example: 
    {
        "action_type": "DATA_SYNC",
        "payload": {"user_id": "123", "scope": "full"}
    }

    Response: Returns a task_id to track progress

2. [GET] /api/v1/status/{task_id}
    Check the pulse of a specific task. (Public)
    Returns: PENDING, RUNNING, COMPLETED, or FAILED.

3. [GET] /docs
    Interactive Swagger UI documentation for testing.