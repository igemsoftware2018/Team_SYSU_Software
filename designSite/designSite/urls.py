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

import account.views

urlpatterns = [
    path('', account.views.index),
    path('admin/', admin.site.urls),
    url(r'^index/?$', account.views.index),
    url(r'^design/?$', design_views.design),
    url(r'^interest/?$', account.views.interest),
    path('login/', account.views.login_view),
    path('register/', account.views.register),
    url(r'^logout/?$', account.views.logout_view),
    path('account/', include('account.urls')),
    path('test/', design_views.test),
] + [
    # API urls
    url(r'api/parts$', design_views.parts),
    url(r'api/part$', design_views.part),
    url(r'api/circuit$', design_views.circuit),
    url(r'api/get_saves$', design_views.get_saves),
    url(r'api/interact$', design_views.interact),
    url(r'api/simulation$', design_views.simulation),
    url(r'api/plasmid_data$', design_views.plasmid_data),
    url(r'api/plasm_part$', design_views.plasm_part),
    url(r'api/sbol_doc$', design_views.get_sbol_doc),
    url(r'api/sbol_json$', design_views.get_sbol_json),
    # url(r'api/tag_favorite$', design_views.tag_favorite),
    # url(r'api/get_favorite$', design_views.get_favorite),
    # url(r'api/part_favorite$', design_views.part_favorite),
    # url(r'api/interest$', main_views.interest),
    # url(r'api/max_safety$', design_views.max_safety),
]

