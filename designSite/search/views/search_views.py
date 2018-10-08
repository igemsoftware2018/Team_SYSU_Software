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
from django.db.models import Q

from design.tools.biode import CIR2ODE as cir2

from django.contrib.auth.decorators import login_required

from django.core.exceptions import ObjectDoesNotExist

from django.views.decorators.csrf import csrf_exempt

import re

import traceback
import logging
logger = logging.getLogger(__name__)

# Create your views here.

@login_required
def search(request):

    def update(w_dict, key, w):
        if key not in w_dict:
            w_dict[key] = 0
        w_dict[key] += 1
    
    search_type = request.GET.get('type')
    if search_type == None:
        return render(reqeust, 'search.html')
    
    try:
        page = request.GET.get('page')
        if page == None:
            page = 1
        page = int(page)
    except:
        return HttpResponseNotFound("Invalid Search!")
        
    if search_type != 'paper' and search_type != 'project':
        return HttpResponseNotFound("Invalid Search!")
    keys = request.GET.get('keyword').lower().split()
    logging.info(keys)
    w_dict = {}
    if search_type == 'project':
        for key in keys:
            if key.isdigit():    # May be year
                q_on_Year = Works.objects.filter(Year__exact=int(key))
            else:
                q_on_Year = Works.objects.none()
            if key == 'gold' or key == 'silver' or key == 'bronze':
                q_on_Medal = Works.objects.filter(Medal__icontains=key)
            else:
                q_on_Medal = Works.objects.none()

            q = Works.objects.filter(Q(Region__icontains=key) | Q(Country__icontains=key))
            q = q | q_on_Medal | q_on_Year
            for obj in q:
                update(w_dict, obj.TeamID, 1)

            q = Works.objects.filter(Award__icontains=key)
            for obj in q:
                update(w_dict, obj.TeamID, 2)
        
            q = Works.objects.filter(Title__icontains=key)
            for obj in q:
                update(w_dict, obj.TeamID, 4)
            
            q = Works.objects.filter(Description__icontains=key)
            for obj in q:
                update(w_dict, obj.TeamID, 1)

            for work in Works.objects.all():
                work_keys = re.split(',|;', work.Keywords)
                for work_key in work_keys:
                    if key in work_key:
                        update(w_dict, work.TeamID, 3)
                        break

    if search_type == 'paper':
        for key in keys:
            try:
                q = Papers.objects.get(DOI__iexact=key)
                update(w_dict, Papers.DOI, 100)
            except:
                pass
            
            q = Papers.objects.filter(Title__icontains=key)
            for obj in q:
                update(w_dict, obj.DOI, 4)
            
            q = Papers.objects.filter(Journal__icontains=key)
            for obj in q:
                update(w_dict, obj.DOI, 1)
            
            for paper in Papers.objects.all():
                if paper.Keywords != 'To be add':
                    paper_keys = re.split(',|;', paper.Keywords)
                    for paper_key in paper_keys:
                        if key in paper_keys:
                            update(w_dict, paper.DOI, 3)
                            break
            
            q = Papers.objects.filter(Authors__icontains=key)
            for obj in q:
                update(w_dict, obj.DOI, 3)
    result = sorted(w_dict, key=lambda x:(-w_dict[x], x))
    context = {
        "NumOfResult": len(result),
        "Type": search_type,
        "Result":[]
    }
    result = result[(page-1) * 10:page * 10]
    
    if search_type == "project":
        for item in result:
            work = Works.objects.get(TeamID=item)
            context['Result'].append({
                "TeamID": work.TeamID,
                "Teamname": work.Teamname,
                "Year": work.Year,
                "Title": work.Title,
                "Description": work.Description,
                "Logo": work.logo,
                "ReadCount": work.ReadCount
            })
    else:
        for item in result:
            paper = Papers.objects.get(DOI=item)
            context['Result'].append({
                "DOI": paper.DOI,
                "Title": paper.Title,
                "Journal": paper.Journal,
                "Author": paper.Authors,
                "Article": paper.ArticleURL,
                "Logo": paper.LogoURL,
            })
    
    return render(request, 'search_result.html', context)
    
        
        
            
        


    # return render(request, 'search.html')


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
                    'name': "unknown",
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