from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
import os

# Header name the Brain must send
API_KEY_NAME = "X-Heart-Signature"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

INTERNAL_SECRET = os.getenv("HEART_INTERNAL_KEY", "codeerax_secret_pulse_2026")

async def validate_brain_request(api_key: str = Security(api_key_header)):
    """
    Validates that the incoming request is actually from the brain API
    """
    if api_key == INTERNAL_SECRET:
        return api_key
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, 
        detail="Invalid Heart Signature. Access Denied."
    )