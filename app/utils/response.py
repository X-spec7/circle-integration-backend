from typing import Any, Dict, Optional
from fastapi.responses import JSONResponse

def success_response(
    data: Any = None,
    message: str = "Success",
    status_code: int = 200
) -> JSONResponse:
    """Create a standardized success response"""
    response_data = {
        "success": True,
        "message": message,
        "data": data
    }
    return JSONResponse(content=response_data, status_code=status_code)

def error_response(
    message: str = "Error",
    status_code: int = 400,
    details: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """Create a standardized error response"""
    response_data = {
        "success": False,
        "message": message,
        "details": details
    }
    return JSONResponse(content=response_data, status_code=status_code) 