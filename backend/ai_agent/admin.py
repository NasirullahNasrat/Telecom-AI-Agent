from django.contrib import admin
from .models import (
    Conversation, Message, TelecomKnowledgeBase,
    InternetPackage, CoverageArea, TechnicalSupportFAQ
)


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
    search_fields = ['question_en', 'question_dari', 'question_pashto', 'answer_en']

    def question_en_short(self, obj):
        return obj.question_en[:50] + '...' if len(obj.question_en) > 50 else obj.question_en


@admin.register(InternetPackage)
class InternetPackageAdmin(admin.ModelAdmin):
    list_display = ['name_en', 'price_afn', 'data_amount', 'validity_days', 'is_active']
    list_filter = ['is_active', 'validity_days']
    search_fields = ['name_en', 'name_dari', 'name_pashto', 'description_en']


@admin.register(CoverageArea)
class CoverageAreaAdmin(admin.ModelAdmin):
    list_display = ['city', 'province', 'coverage_type', 'status']
    list_filter = ['coverage_type', 'status', 'province']
    search_fields = ['city', 'province', 'notes_en']


@admin.register(TechnicalSupportFAQ)
class TechnicalSupportFAQAdmin(admin.ModelAdmin):
    list_display = ['category', 'question_en_short', 'is_published', 'created_at']
    list_filter = ['category', 'is_published', 'created_at']
    search_fields = ['question_en', 'question_dari', 'question_pashto', 'answer_en']

    def question_en_short(self, obj):
        return obj.question_en[:50] + '...' if len(obj.question_en) > 50 else obj.question_en
