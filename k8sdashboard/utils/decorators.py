from functools import wraps
from django.shortcuts import redirect
from django.urls import reverse

def login_required(view_func):
    """Decorator to ensure the user is logged in."""

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        print('Decorators: executing before the function......')
        
        current_username = request.session.get('username', None)
        if current_username is None:
            return redirect('/login')

        # if not request.user.is_authenticated:
            # return redirect(reverse('login'))  # Redirect to login page
        return view_func(request, *args, **kwargs)

    return wrapper