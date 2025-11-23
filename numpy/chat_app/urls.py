from django.urls import path
from . import views


urlpatterns = [
    path('', views.chat, name='chat'),
    path('process/', views.process, name='process')
]