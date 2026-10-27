from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
from app.core.config import settings

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)
INTERNAL_TOKEN_HEADER = APIKeyHeader(name="X-Internal-Token", auto_error=False)

def get_current_user_or_api_key(api_key: str = Security(API_KEY_HEADER)):
    if not settings.API_KEY_ENABLED:
        # Default dev user identifier
        return {"user_id": "00000000-0000-0000-0000-000000000001", "role": "developer"}
    
    if not api_key or api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-API-Key"
        )
    return {"user_id": "00000000-0000-0000-0000-000000000001", "role": "authenticated_user"}

def verify_internal_automation_token(token: str = Security(INTERNAL_TOKEN_HEADER)):
    if not token or token != settings.INTERNAL_AUTOMATION_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid internal automation token"
        )
    return True
