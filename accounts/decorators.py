from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from functools import wraps

def staff_required(view_func):
    @wraps(view_func)
    @login_required(login_url='/accounts/login/')
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('/accounts/login/')
        return view_func(request, *args, **kwargs)
    return wrapped_view
