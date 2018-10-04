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


def takeTime(elem):
    return elem.Update_time


@login_required
def personal_index(request):
    user = request.user
    username = user.username
    part_query = Parts.objects.filter(Username=username)
    circuit_query = Circuit.objects.filter(
        Author=user).order_by('-Update_time')
    authority_query = Authorities.objects.filter(User=user)

    parts = [{
        'ID': x.id,
        'Name': x.Name,
        'Role': x.Role,
        'Type': x.Type,
        'Description': x.Description
    } for x in part_query]

    circuits = []
    distinct = []
    for item in circuit_query:
        temp = item.Name
        if temp not in distinct:
            distinct.append(temp)
            circuits.append({
                'ID': item.id,
                'Name': item.Name,
                'Author': item.Author.username,
                'Description': item.Description,
                'LastEditor': item.Editor.username,
                'LastUpdateTime': item.Update_time
            })

    shared_circuits = []
    items = []
    for x in authority_query:
        circuit_list = Circuit.objects.filter(
            pk=x.Circuit_id).order_by('-Update_time')
        for item in circuit_list:
            temp = item.Name
            if temp not in items:
                items.append(temp)
                shared_circuits.append({
                    'ID': circuit_list[0].id,
                    'Name': circuit_list[0].Name,
                    'Author': circuit_list[0].Author.username if not circuit_list[0].Editor is None else 'None',
                    'Description': circuit_list[0].Description,
                    'Authority': x.Authority,
                    'LastEditor': circuit_list[0].Editor.username if not circuit_list[0].Editor is None else 'None',
                    'LastUpdateTime': circuit_list[0].Update_time
                })


    circuit_query.order_by('-id')
    authority_circuits = []
    for item in circuit_query:
            authority_circuits.append({
                'ID': item.id,
                'Name': item.Name,
                'Author': item.Author.username,
                'Description': item.Description,
                'LastEditor': item.Editor.username,
                'LastUpdateTime': item.Update_time
            })

    return render(request, 'personal_index.html', {
        'parts': parts,
        'circuits': circuits,
        'share': shared_circuits,
        'authority': authority_circuits
    })


def signin_view(request):
    if request.method == "POST":
        # Login action
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            print(username, password)
            user = authenticate(username=username, password = password)
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
                    username=form.cleaned_data['username'],
                    email=form.cleaned_data["email"],
                    password=form.cleaned_data["password"],
                    org=form.cleaned_data["org"],
                    igem=form.cleaned_data["igem"]
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
