from flask import jsonify
from exceptions.custom_exceptions import AppError

class BaseController:
    """
    Base Controller to centralize common logic like response formatting and error handling.
    """
    
    @staticmethod
    def success_response(data=None, message="Success", status_code=200):
        """
        Returns a standardized success JSON response.
        Structure:
        {
            "status": "success",
            "message": "...",
            "data": { ... }
        }
        """
        response_body = {
            "ok": True,
            "status": "success",
            "message": message,
            "data": data
        }
        return jsonify(response_body), status_code

    @staticmethod
    def error_response(message="An error occurred", status_code=500, data=None):
        """
        Returns a standardized error JSON response.
        Structure:
        {
            "status": "error",
            "message": "..."
        }
        """
        response_body = {
            "ok": False,
            "status": "error",
            "message": message,
            # Back-compat for older frontend code that reads `error`
            "error": message,
            "data": data,
        }
        return jsonify(response_body), status_code

    def handle_exception(self, e):
        """
        Centralized exception handler.
        Maps Custom Exceptions (AppError) to their specific status codes.
        Maps unknown exceptions to 500 Internal Server Error.
        """
        if isinstance(e, AppError):
            return self.error_response(message=e.message, status_code=e.code)
        
        # Log the unexpected error here in a real app
        # print(f"Unexpected Error: {e}") 
        return self.error_response(message="Internal Server Error", status_code=500)
