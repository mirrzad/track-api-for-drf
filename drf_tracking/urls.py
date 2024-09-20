from django.urls import path
from . import views


app_name = 'drf_tracking'

urlpatterns = [
    path('', views.Home.as_view(), name='home')
]
