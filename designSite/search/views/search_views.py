# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
from django.shortcuts import render, redirect
from django.http import HttpRequest

import json
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound,\
    HttpResponseForbidden
from django.contrib import messages

# from design.models import *
from design.models.bio import *
from design.models.user import *


from design.tools.biode import CIR2ODE as cir2

from django.contrib.auth.decorators import login_required

from django.core.exceptions import ObjectDoesNotExist

from django.views.decorators.csrf import csrf_exempt

import traceback
import logging
logger = logging.getLogger(__name__)

# Create your views here.

@login_required
def search(request):
    return render(request, 'search.html')


@login_required
def work(request):
    try:
        wk = Works.objects.get(TeamID = request.GET.get('id'))
        use_parts = wk.Use_parts.split(';')
        part = []
        for item in use_parts:
            try:
                pt = Parts.objects.get(Name = item)
                part.append({
                    'id': request.GET.get('id'),
                    'BBa': item,
                    'name': pt.secondName,
                })
            except Parts.DoesNotExist:
                part.append({
                    'id': request.GET.get('id'),
                    'BBa': item,
                    'name': "None",
                })
        if wk.Img.all().count() == 0:
            Img = [wk.DefaultImg]
        else:
            Img = [i.URL for i in wk.Img.all()]

        Awards = wk.Award.split(';')
        while len(Awards) > 0 and Awards[-1] == '':
            Awards = Awards[: -1]

        relatedTeams = Trelation.objects.filter(first = wk)
        relatedTeams = list(map(lambda rt: {
            'teamName': rt.second.Teamname,
            'projectName': rt.second.Title,
            'year': rt.second.Year,
            'id': rt.second.TeamID
        }, relatedTeams))

        keywords = TeamKeyword.objects.filter(Team = wk)
        keywords = list(map(lambda tk: [tk.keyword, tk.score], keywords))
        keywords.sort(key = lambda tk: -tk[1])
        keywords = list(map(lambda tk: tk[0], keywords))[:5]

        wk.ReadCount += 1
        wk.save()
        context = {
            'projectName': wk.Title,
            'teamName': wk.Teamname,
            'year': wk.Year,
            'readCount': wk.ReadCount,
            'medal': wk.Medal,
            'rewards': Awards,
            'description': wk.Description,
            'images': Img,
            'designId': -1 if wk.Circuit is None else wk.Circuit.id,
            'part': part,
            'logo': wk.logo,
            'keywords': keywords,
            'relatedTeams': relatedTeams
        }
        return render(request, 'work.html', context)

    except Works.DoesNotExist:
        return HttpResponse("Work Does Not Exist!")


@login_required
def paper(request):
    key = request.GET.get('id')
    try:
        paper = Papers.objects.get(pk = key)
        parts_query = CircuitParts.objects.filter(Circuit = paper.Circuit)
        part = []
        for q in parts_query:
            pt = q.Part
            part.append({
                'id': pt.id,
                'BBa': pt.Name,
                'name': pt.secondName})
        context = {
            'title': paper.Title,
            'DOI': paper.DOI,
            'authors': paper.Authors.split(','),
            'abstract': paper.Abstract,
            'JIF': paper.JIF,
            'keywords': paper.Keywords,
            'designId': paper.Circuit.id,
            'articleURL': paper.ArticleURL,
            'copyright': paper.Copyright,
            'part': part
        }
        
        return render(request, 'paper.html', context)
    except Papers.DoesNotExist:
        return HttpResponse('Does not exist.')