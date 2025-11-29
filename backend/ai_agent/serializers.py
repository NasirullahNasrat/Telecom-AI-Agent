from rest_framework import serializers
from .models import Conversation, Message

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