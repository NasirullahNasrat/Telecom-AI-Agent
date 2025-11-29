from django.db import models
import uuid

class Conversation(models.Model):
    LANGUAGES = [
        ('en', 'English'),
        ('fa', 'Dari'),
        ('ps', 'Pashto'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_id = models.CharField(max_length=255, unique=True)
    user_language = models.CharField(max_length=10, choices=LANGUAGES, default='en')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Conversation {self.session_id} ({self.user_language})"

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    is_user = models.BooleanField(default=True)
    intent = models.CharField(max_length=100, blank=True)
    confidence = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']

class TelecomKnowledgeBase(models.Model):
    CATEGORIES = [
        ('balance', 'Balance & Payments'),
        ('packages', 'Internet Packages'),
        ('coverage', 'Network Coverage'),
        ('sim', 'SIM Registration'),
        ('technical', 'Technical Support'),
    ]
    
    question_en = models.TextField()
    question_dari = models.TextField()
    question_pashto = models.TextField()
    answer_en = models.TextField()
    answer_dari = models.TextField()
    answer_pashto = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORIES)
    created_at = models.DateTimeField(auto_now_add=True)