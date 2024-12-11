from django.conf import settings
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied

def login_prohibited(view_function):
    """Decorator for view functions that redirect users away if they are logged in."""
    
    def modified_view_function(request):
        if request.user.is_authenticated:
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            return view_function(request)
    return modified_view_function

def is_admin(function):
    """Decorator to check if the user is an admin."""
    def wrap(request, *args, **kwargs):
        if request.user.role != 'admin':
            raise PermissionDenied  # Redirect to home or a custom error page
        return function(request, *args, **kwargs)
    return wrap

def is_tutor(function):
    """Decorator to check if the user is a tutor."""
    def wrap(request, *args, **kwargs):
        if request.user.role != 'tutor':
            raise PermissionDenied  # Redirect to home or a custom error page
        return function(request, *args, **kwargs)
    return wrap

def is_student(function):
    """Decorator to check if the user is a student."""
    def wrap(request, *args, **kwargs):
        if request.user.role != 'student':
            raise PermissionDenied  # Redirect to home or a custom error page
        return function(request, *args, **kwargs)
    return wrap