from django.conf import settings
from django.http import HttpResponseForbidden
from django.shortcuts import redirect

def login_prohibited(view_function):
    """Decorator for view functions that redirect users away if they are logged in."""
    
    def modified_view_function(request):
        if request.user.is_authenticated:
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            return view_function(request)
    return modified_view_function

def admin_required(view_function):
    """Decorator to restrict a view to admin users."""

    def modified_view_function(request, *args, **kwargs):
        if not request.user.is_staff: 
            return HttpResponseForbidden("You do not have the necessary permissions to view this page.")
        else:
            return view_function(request, *args, **kwargs)
    
    return modified_view_function