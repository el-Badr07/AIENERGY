import logging
import traceback
from typing import Dict, Any, Tuple, Optional
from functools import wraps
from flask import jsonify, current_app

logger = logging.getLogger(__name__)

class APIError(Exception):
    """Base class for API errors"""
    
    def __init__(self, message: str, status_code: int = 400, payload: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.payload = payload
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for JSON response"""
        result = dict(self.payload or {})
        result['error'] = self.message
        return result

class ValidationError(APIError):
    """Error for validation failures"""
    
    def __init__(self, message: str, payload: Optional[Dict[str, Any]] = None):
        super().__init__(message, 400, payload)

class NotFoundError(APIError):
    """Error for resource not found"""
    
    def __init__(self, message: str, payload: Optional[Dict[str, Any]] = None):
        super().__init__(message, 404, payload)

class ProcessingError(APIError):
    """Error for processing failures"""
    
    def __init__(self, message: str, payload: Optional[Dict[str, Any]] = None):
        super().__init__(message, 500, payload)

def handle_api_error(error: APIError) -> Tuple[Dict[str, Any], int]:
    """
    Handle API errors and return appropriate JSON response
    
    Args:
        error: The API error
        
    Returns:
        Tuple of (JSON response, status code)
    """
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

def error_handler(f):
    """
    Decorator for API route functions to handle errors
    
    Args:
        f: The function to decorate
        
    Returns:
        Decorated function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except APIError as e:
            logger.warning(f"API Error: {str(e)}")
            return handle_api_error(e)
        except Exception as e:
            logger.error(f"Unhandled exception: {str(e)}")
            logger.error(traceback.format_exc())
            
            # In development mode, include the traceback in the error
            if current_app.debug:
                error = ProcessingError(str(e), {"traceback": traceback.format_exc()})
            else:
                error = ProcessingError("An unexpected error occurred")
                
            return handle_api_error(error)
    
    return decorated_function
