# backend/app/core/utils/error_handler.py

import functools
import logging
from typing import Callable, Any, Dict

# Configure basic logging for now. In a real app, this would be more sophisticated.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class APIError(Exception):
    """Custom exception for API-related errors."""
    def __init__(self, message: str, status_code: int = 500, details: Any = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details

    def to_dict(self) -> Dict[str, Any]:
        return {
            "message": self.message,
            "status_code": self.status_code,
            "details": self.details
        }

def error_handler_decorator(func: Callable) -> Callable:
    """
    Decorator for handling errors in FastAPI endpoints or core logic functions.
    It logs the error in a structured format and returns a user-friendly APIError response.
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        try:
            # If the original function is an async function, await it
            if inspect.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
        except APIError as e:
            # Custom APIError, log and re-raise (or return appropriate response)
            logger.error(
                "API Error caught in %s: %s",
                func.__name__,
                e.message,
                exc_info=True,
                extra={"status_code": e.status_code, "details": e.details}
            )
            raise e # Re-raise to be caught by FastAPI's exception handlers
        except Exception as e:
            # Catch all other unexpected errors
            error_message = "An unexpected error occurred."
            status_code = 500
            
            # Attempt to extract a more specific message if available
            if hasattr(e, 'detail'): # Common for HTTPException in FastAPI
                error_message = e.detail
            elif str(e):
                error_message = str(e)

            logger.error(
                "Unhandled exception in %s: %s",
                func.__name__,
                error_message,
                exc_info=True,
                extra={"original_exception_type": type(e).__name__}
            )
            # You might want to return a standardized error response here,
            # or raise a new APIError which FastAPI can then handle.
            raise APIError(
                message=f"Internal Server Error: {error_message}",
                status_code=status_code,
                details={"function": func.__name__, "error_type": type(e).__name__}
            )
    return wrapper

import inspect # Import inspect for checking coroutine function

# Example usage (for demonstration, can be removed in final version)
if __name__ == "__main__":
    # Example functions to demonstrate the decorator
    @error_handler_decorator
    def my_sync_function(should_fail: bool):
        if should_fail:
            raise ValueError("Something went wrong in sync function!")
        return {"status": "success", "data": "Sync data"}

    @error_handler_decorator
    async def my_async_function(should_fail: bool):
        if should_fail:
            raise APIError("Custom API error in async function!", status_code=400, details={"code": "BAD_REQUEST"})
        return {"status": "success", "data": "Async data"}

    # Test sync function
    print("--- Testing Sync Function ---")
    try:
        print(my_sync_function(False))
        # print(my_sync_function(True)) # This would raise an APIError
    except APIError as e:
        print(f"Caught APIError: {e.to_dict()}")
    except Exception as e:
        print(f"Caught unexpected exception: {e}")

    # Test async function (requires an async context to run)
    print("\n--- Testing Async Function ---")
    import asyncio
    async def run_async_tests():
        try:
            print(await my_async_function(False))
            # print(await my_async_function(True)) # This would raise an APIError
        except APIError as e:
            print(f"Caught APIError: {e.to_dict()}")
        except Exception as e:
            print(f"Caught unexpected exception: {e}")

    asyncio.run(run_async_tests())
