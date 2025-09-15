from typing import Any, Dict, Optional
from fastapi.responses import JSONResponse


def success_response(data: Any = None, message: str = "Success") -> Dict[str, Any]:
    """Create a standardized success response"""
    response = {
        "success": True,
        "message": message
    }
    if data is not None:
        response["data"] = data
    return response


def error_response(message: str = "An error occurred", error_code: Optional[str] = None) -> Dict[str, Any]:
    """Create a standardized error response"""
    response = {
        "success": False,
        "message": message
    }
    if error_code:
        response["error_code"] = error_code
    return response


def validation_error_response(errors: Dict[str, Any]) -> Dict[str, Any]:
    """Create a validation error response"""
    return {
        "success": False,
        "message": "Validation failed",
        "errors": errors
    }


def create_response(status_code: int, content: Dict[str, Any]) -> JSONResponse:
    """Create a FastAPI JSONResponse with proper status code"""
    return JSONResponse(status_code=status_code, content=content)


# Common HTTP status codes and their responses
def bad_request(message: str = "Bad request") -> JSONResponse:
    return create_response(400, error_response(message, "BAD_REQUEST"))


def unauthorized(message: str = "Unauthorized") -> JSONResponse:
    return create_response(401, error_response(message, "UNAUTHORIZED"))


def forbidden(message: str = "Forbidden") -> JSONResponse:
    return create_response(403, error_response(message, "FORBIDDEN"))


def not_found(message: str = "Not found") -> JSONResponse:
    return create_response(404, error_response(message, "NOT_FOUND"))


def conflict(message: str = "Conflict") -> JSONResponse:
    return create_response(409, error_response(message, "CONFLICT"))


def internal_server_error(message: str = "Internal server error") -> JSONResponse:
    return create_response(500, error_response(message, "INTERNAL_ERROR"))


def ok(data: Any = None, message: str = "Success") -> JSONResponse:
    return create_response(200, success_response(data, message))


def created(data: Any = None, message: str = "Created successfully") -> JSONResponse:
    return create_response(201, success_response(data, message))