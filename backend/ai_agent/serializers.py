from rest_framework import serializers
from .models import (
    Conversation, Message, TelecomKnowledgeBase,
    InternetPackage, CoverageArea, TechnicalSupportFAQ,
    AppConfig
)


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'content', 'is_user', 'intent', 'confidence', 'created_at']


class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = ['id', 'session_id', 'user_language', 'created_at', 'updated_at', 'messages']


class ChatRequestSerializer(serializers.Serializer):
    message = serializers.CharField(required=True)
    session_id = serializers.CharField(required=False, default='default')
    language = serializers.ChoiceField(choices=Conversation.LANGUAGES, default='en')


class VoiceChatRequestSerializer(serializers.Serializer):
    session_id = serializers.CharField(required=False, default='default')
    language = serializers.ChoiceField(choices=Conversation.LANGUAGES, default='en')
    text = serializers.CharField(required=False)


# --- Admin / CRUD Serializers ---

class TelecomKnowledgeBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelecomKnowledgeBase
        fields = '__all__'


class InternetPackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = InternetPackage
        fields = '__all__'


class CoverageAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoverageArea
        fields = '__all__'


class TechnicalSupportFAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = TechnicalSupportFAQ
        fields = '__all__'


class AppConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppConfig
        fields = ['key', 'value', 'updated_at']
