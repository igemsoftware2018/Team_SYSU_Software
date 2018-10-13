"""designSite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from django.conf.urls import include
from design.views import design_views
from search.views import search_views
from account.views import account_views

import account.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('search/', search_views.search),
    path('paper/', search_views.paper),
    path('', account_views.index),
    path('login/', account_views.signin_view),
    path('signin/', account_views.signin_view),
    path('signup/', account_views.signup),
    path('account/', include('account.urls')),
    url(r'^index/?$', account_views.personal_index),
    url(r'^design/?$', design_views.design),
    url(r'^design/\d+/?$', design_views.personal_design),
    url(r'^design/realtime/\d+/?$', design_views.personal_design),
    url(r'^design/share/\d+/?$', design_views.share_design),
    url(r'^design/share/realtime/\d+/?$', design_views.share_design),
    url(r'^work$', search_views.work),
    url(r'^search$', search_views.search),
    url(r'^interest/?$', account_views.interest),
    url(r'^logout/?$', account_views.logout_view),
] + [
    # API urls
    url(r'api/users$', design_views.users),
    url(r'api/authority$', design_views.authority),
    url(r'api/authority_delete$', design_views.authority_delete),
    url(r'api/authority_circuits$', design_views.authority_circuits),
    url(r'api/parts$', design_views.parts),
    url(r'api/part$', design_views.part),
    url(r'api/circuits$', design_views.circuits),
    url(r'api/circuit$', design_views.circuit),
    url(r'api/get_saves$', design_views.get_saves),
    # url(r'api/plasmid_data$', design_views.plasmid_data),
    # url(r'api/plasm_part$', design_views.plasm_part),
    url(r'api/sbol_doc$', design_views.get_sbol_doc),
    url(r'api/sbol_json$', design_views.get_sbol_json),
    url(r'api/chassis$', design_views.chassis),
    url(r'api/analysis$', design_views.analysis_sequence),
    url(r'api/realtime/\d+/?$', design_views.api_real_time),
    url(r'api/liveCanvas/\d+/.*?$', design_views.api_live_canvas),
    url(r'api/simulation$', design_views.sim_and_opt),
    # url(r'api/interact$', design_views.interact),
    # url(r'api/tag_favorite$', design_views.tag_favorite),
    # url(r'api/get_favorite$', design_views.get_favorite),
    # url(r'api/part_favorite$', design_views.part_favorite),
    # url(r'api/interest$', main_views.interest),
    # url(r'api/max_safety$', design_views.max_safety),
]

