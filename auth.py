# user_service/auth.py
from fastapi import Request, HTTPException, Depends
from fastapi.security import APIKeyHeader
import os

X_API_GATEWAY = APIKeyHeader(name="X-From-Gateway", auto_error=False)
GATEWAY_SECRET = os.getenv("GATEWAY_SECRET", "your-secret-shared-key")
ALLOWED_PATHS = [
    "/health",  
    "/metrics"  
]

async def verify_gateway_request(
    request: Request,
    x_api_gateway: str = Depends(X_API_GATEWAY)
):
    """
    Middleware to ensure requests only come from the API Gateway
    or are accessing allowed monitoring endpoints
    """
    # Allow health check and metrics endpoints without authentication
    for path in ALLOWED_PATHS:
        if request.url.path.startswith(path):
            return True
    
    # For all other paths, verify the gateway header is present and correct
    if not x_api_gateway or x_api_gateway != "true":
        raise HTTPException(
            status_code=403,
            detail="Direct access to service is forbidden. Please use the API Gateway."
        )
    
    # Optional: Add additional security by checking a secret key
    # shared_secret = request.headers.get("X-Gateway-Secret")
    # if not shared_secret or shared_secret != GATEWAY_SECRET:
    #    raise HTTPException(status_code=403, detail="Invalid gateway authentication")
    
    return True