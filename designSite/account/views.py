from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from design.models.bio import *
import traceback
import logging
logger = logging.getLogger(__name__)

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


@login_required
def personal_index(request):
    # TODO: query parts and circuits
    user = request.user
    username = user.username
    part_query = Parts.objects.filter(Username=username)
    circuit_query = Circuit.objects.filter(Author=user)

    parts = [{
        'ID': x.id,
        'Name': x.Name,
        'Role': x.Role,
        'Description': x.Description
    } for x in part_query]
    circuits = [{
        'ID': x.id,
        'Name': x.Name,
        'Version': 0, #TODO: no version.
        'Description': x.Description
    } for x in circuit_query]
    logger.debug(part_query)
    logger.debug(circuit_query)
    return render(request, 'personal_index.html', {'parts': parts, 'circuits': circuits})


def signin_view(request):
    if request.method == "POST":
        # Login action
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            print(username, password)
            user = authenticate(username = username, password = password)
            if user is not None:
                login(request, user)
                # messages.success(request, "Login successfully!")
                next_url = request.POST.get('next')
                logger.debug(str(next_url))
                if next_url:
                    return redirect(next_url)
                else:
                    return redirect('/')
            else:
                messages.error(request, "Invalid Login")
        else:
            messages.error(request, Inv)
        return render(request, "signin.html")
    elif request.method == "GET":
        return render(request, 'signin.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('/')

@login_required
def interest_view(request):
    return render(request, 'interest.html')


def signup(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                user = User.objects.create_user(
                    username = form.cleaned_data['username'],
                    email = form.cleaned_data["email"],
                    password = form.cleaned_data["password"],
                    org = form.cleaned_data["org"],
                    igem = form.cleaned_data["igem"]
                )
                login(request, user)
                # messages.success(request, "Register successfully!")
                return redirect('/index')
            except IntegrityError:
                messages.error(request, "Email already exists!")
            except:
                messages.error(request, Err)
        else:
            messages.error(request, Inv)
    return render(request, 'signup.html')