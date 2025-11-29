from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

def login_view(request):
    return render(request, 'accounts/login.html')


def logout_view(request):
    return render(request, 'accounts/logout.html')


@login_required
def dashboard(request):
    return render(request, 'accounts/dashboard.html')


