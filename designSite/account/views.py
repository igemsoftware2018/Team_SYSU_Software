from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

# from account.models import *

from design.models import *

from account.forms import LoginForm, RegisterForm
# Create your views here.

import json

Err = "Something wrong!"
Inv = "Invalid form!"


# *interest* is only for test
def interest(request):
    return render(request, 'interest.html')


def index(request):
    return render(request, 'index.html')

def login_view(request):
    if request.user.is_authenticated:
        print("hahahahahah")
    if request.method == "POST":
        # Login action
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            print(email, password)
            user = authenticate(username = email, password = password)
            if user is not None:
                login(request, user)
                print("Login successfully!")
                messages.success(request, "Login successfully!")
                next_url = request.POST.get('next')
                if next_url:
                    return redirect(next_url)
                else:
                    return redirect('/')
            else:
                messages.error(request, "Invalid Login")
        else:
            messages.error(request, Inv)
        return render(request, "login.html")
    elif request.method == "GET":
        return render(request, 'login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('/index')

@login_required
def interest_view(request):
    return render(request, 'interest.html')

def register(request):
    if request.method == "POST":
        print("REQUEST:")
        print(request)
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                user = User.objects.create_user(email = form.cleaned_data["email"],
                        password = form.cleaned_data["password"],
                        org = form.cleaned_data["org"],
                        igem = form.cleaned_data["igem"]
                        )
                login(request, user)
                messages.success(request, "Register successfully!")
                return redirect('/index')
            except IntegrityError:
                messages.error(request, "Email already exists!")
            except:
                messages.error(request, Err)
        else:
            messages.error(request, Inv)
    return render(request, 'register.html')