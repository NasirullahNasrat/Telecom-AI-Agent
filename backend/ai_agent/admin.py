from django.contrib import admin
from .models import Conversation, Message, TelecomKnowledgeBase

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'user_language', 'created_at']
    list_filter = ['user_language', 'created_at']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['conversation', 'content_short', 'is_user', 'created_at']
    list_filter = ['is_user', 'created_at']
    
    def content_short(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content

@admin.register(TelecomKnowledgeBase)
class TelecomKnowledgeBaseAdmin(admin.ModelAdmin):
    list_display = ['category', 'question_en_short', 'created_at']
    list_filter = ['category', 'created_at']
    
    def question_en_short(self, obj):
        return obj.question_en[:50] + '...' if len(obj.question_en) > 50 else obj.question_en