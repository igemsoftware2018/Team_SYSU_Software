from django.urls import path

from .views import account_views
app_name = 'account'

urlpatterns = [
    path('', account_views.personal_index),
]