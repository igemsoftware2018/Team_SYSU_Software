# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import logging
import os
import re
import traceback

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import (HttpRequest, HttpResponse, HttpResponseForbidden,
                         HttpResponseNotFound, JsonResponse)
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt

from design.models.bio import *
from design.models.user import *
from design.tools.biode import CIR2ODE as cir2

# from search.nn_search.nn_search import recommend_team

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
        return render(request, 'search.html')
    
    # try:
    #     page = request.GET.get('page')
    #     if page == None:
    #         page = 1
    #     page = int(page)
    # except:
    #     return HttpResponseNotFound("Invalid Search!")


    ugly_photo_list = ["static\img\Team_img\\none.jpg", "http://2013.igem.org\\wiki/skins/common/images/wiki.jpg", "http://2014.igem.org/images/wiki.png", "http://2012.igem.org\\wiki/skins/common/images/wiki.png", "http://2010.igem.org/images/wiki.png", "http://2009.igem.org\wiki/skins/common/images/wiki.png", "http://2011.igem.org\wiki/skins/common/images/wiki.png"]

    if search_type != 'paper' and search_type != 'project':
        return HttpResponseNotFound("Invalid Search!")
    keys = request.GET.get('keyword').lower().split()
    logging.info(keys)
    w_dict = {}
    if search_type == 'project':
        if search.nn_search_flag >= 0:
            #TODO: I change here.
            try:
                nn_search_result = recommend_team(keys[0])
                search.nn_search_flag = 1   # nn_search module is initialized successfully
                logging.info("Search module activated!")
            except:
                logging.info("Unable to load nn search module.")
                search.nn_search_flag = -1  ## nn_search module failed
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

            q = Works.objects.filter(Teamname__icontains=key)
            for obj in q:
                update(w_dict, obj.TeamID, 3)
        
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

            for i in w_dict:
                work = Works.objects.get(TeamID=i)
                if work.logo not in ugly_photo_list:
                    update(w_dict, work.TeamID, 3)
                    

    elif search_type == 'paper':
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

            for i in w_dict:
                paper = Papers.objects.get(DOI=i)
                if paper.LogoURL not in ugly_photo_list:
                    update(w_dict, paper.DOI, 3)

        

    result = sorted(w_dict, key=lambda x:(-w_dict[x], x))
    result = result[0:min(len(result), 50)]
    context = {
        "NumOfResult": len(result),
        "IsProject": search_type == "project",
        "IsPaper": search_type == "paper",
        "Result":[]
    }

    # result = result[(page-1) * 10:page * 10]
    

    if search_type == "project":
        for item in result:
            work = Works.objects.get(TeamID=item)
            des =  work.Description[0:min(250, len(work.Description))]
            if len(work.Description) > 300:
                while des[-1] != ' ':
                    des = des[:-1]
                des += '...'
            logo = work.logo
            if logo in ugly_photo_list:
                logo = "/static/img/Team_Img/none.jpg"
            context['Result'].append({
                "TeamID": work.TeamID,
                "Teamname": work.Teamname,
                "Year": work.Year,
                "Title": work.Title,
                "Description": des,
                "Logo": logo,
                "ReadCount": work.ReadCount
            })
    else:
        for item in result:
            paper = Papers.objects.filter(DOI=item)
            id = paper.values("pk")[0]['pk']
            paper = paper[0]
            context['Result'].append({
                "ID": id,
                "DOI": paper.DOI,
                "Title": paper.Title,
                "Journal": paper.Journal,
                "Author": paper.Authors,
                "Article": paper.ArticleURL,
                "Logo": paper.LogoURL,
            })
    # logging.info(context)
    return render(request, 'search_result.html', context)
search.nn_search_flag = 0


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
        if wk.Circuit:
            circuitID = Circuit.objects.filter(Name = wk.Circuit.Name).values('pk')[0]['pk']
        else:
            circuitID = 0
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
            'relatedTeams': relatedTeams,
            'circuitID': circuitID,
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
