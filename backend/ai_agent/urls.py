from django.urls import path
from . import views

urlpatterns = [
    path('chat/', views.chat_endpoint, name='chat'),
    path('voice-chat/', views.voice_chat_endpoint, name='voice-chat'),
    path('health/', views.health_check, name='health-check'),
]