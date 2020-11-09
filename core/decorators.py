from django.http import HttpResponse
from django.shortcuts import redirect

# If user is already authenticated, redirect to homepage.
# Otherwise go with views's function.
def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('core:home')
        else:
            return view_func(request, *args, **kwargs)

    return wrapper_func