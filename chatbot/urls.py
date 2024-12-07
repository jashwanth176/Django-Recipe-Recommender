from django.urls import path
from . import views

urlpatterns = [
    path('chatbot/', views.chatbot, name='chatbot'),
    path('check_audio_status/', views.check_audio_status, name='check_audio_status'),
    path('get_audio/', views.get_audio, name='get_audio'),
]
