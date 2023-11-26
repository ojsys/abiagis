from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from django.contrib.auth import login as auth_login, logout
# Create your views here.


def login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('index')
            
    else:
        form = CustomAuthenticationForm()
    return render(request, 'account/login.html', {
        'title': 'ABIAGIS', 
        'form': form
    })


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('index')
    else:
        form = CustomUserCreationForm()
    return render(request, 'account/register.html', {
        'title': 'ABIAGIS', 
        'form': form
    })

def logout_view(request):
    logout(request)
    return redirect('login')