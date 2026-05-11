from django.urls import path
from . import views

urlpatterns = [
    # Chat & Voice
    path('chat/', views.chat_endpoint, name='chat'),
    path('voice-chat/', views.voice_chat_endpoint, name='voice-chat'),
    path('health/', views.health_check, name='health-check'),

    # Admin Login
    path('admin/login/', views.admin_login, name='admin-login'),

    # Admin CRUD - Knowledge Base
    path('admin/knowledge-base/', views.knowledge_base_list, name='kb-list'),
    path('admin/knowledge-base/<int:pk>/', views.knowledge_base_detail, name='kb-detail'),

    # Admin CRUD - Internet Packages
    path('admin/packages/', views.internet_package_list, name='package-list'),
    path('admin/packages/<int:pk>/', views.internet_package_detail, name='package-detail'),

    # Admin CRUD - Coverage Areas
    path('admin/coverage/', views.coverage_area_list, name='coverage-list'),
    path('admin/coverage/<int:pk>/', views.coverage_area_detail, name='coverage-detail'),

    # Admin CRUD - Technical Support FAQs
    path('admin/faqs/', views.faq_list, name='faq-list'),
    path('admin/faqs/<int:pk>/', views.faq_detail, name='faq-detail'),

    # Admin Dashboard Stats
    path('admin/stats/', views.admin_stats, name='admin-stats'),

    # Admin Settings (API Key Configuration)
    path('admin/settings/', views.admin_settings, name='admin-settings'),

    # Text-to-Speech (API-based for Dari/Pashto support)
    path('tts/status/', views.tts_status, name='tts-status'),
    path('tts/speak/', views.tts_speak, name='tts-speak'),
]
