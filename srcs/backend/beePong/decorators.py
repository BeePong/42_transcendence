from django.http import JsonResponse
from functools import wraps

def login_required_json(view_func):
    """
    A decorator that checks if the user is authenticated before allowing access to the view.
    
    If the user is not authenticated, it returns a JSON response with a status code of 401.
    If the user is authenticated, it calls the original view function.
    
    Args:
        view_func: The view function to be wrapped by the decorator.

    Returns:
        A wrapped view function that enforces authentication.
    """
    @wraps(view_func)  # Preserve the original function's metadata (like its name and docstring)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'authenticated': False}, status=401)
        # Call the original view function with the request and any additional arguments
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view  # Return the wrapped view function