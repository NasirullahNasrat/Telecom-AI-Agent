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
    question_dari = models.TextField(blank=True, default='')
    question_pashto = models.TextField(blank=True, default='')
    answer_en = models.TextField()
    answer_dari = models.TextField(blank=True, default='')
    answer_pashto = models.TextField(blank=True, default='')
    category = models.CharField(max_length=20, choices=CATEGORIES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.category}] {self.question_en[:60]}"


class InternetPackage(models.Model):
    name_en = models.CharField(max_length=200)
    name_dari = models.CharField(max_length=200, blank=True, default='')
    name_pashto = models.CharField(max_length=200, blank=True, default='')
    price_afn = models.DecimalField(max_digits=10, decimal_places=2)
    data_amount = models.CharField(max_length=50, help_text="e.g. 1GB, 3GB, 10GB")
    validity_days = models.IntegerField(help_text="Number of days the package is valid")
    description_en = models.TextField(blank=True, default='')
    description_dari = models.TextField(blank=True, default='')
    description_pashto = models.TextField(blank=True, default='')
    activation_code = models.CharField(max_length=50, blank=True, default='', help_text="USSD code to activate, e.g. *123*1#")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['price_afn']

    def __str__(self):
        return f"{self.name_en} - {self.price_afn} AFN ({self.data_amount})"


class CoverageArea(models.Model):
    COVERAGE_TYPES = [
        ('2g', '2G'),
        ('3g', '3G'),
        ('4g', '4G'),
        ('5g', '5G'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('planned', 'Planned'),
        ('maintenance', 'Under Maintenance'),
    ]

    province = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    coverage_type = models.CharField(max_length=10, choices=COVERAGE_TYPES, default='4g')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    notes_en = models.TextField(blank=True, default='')
    notes_dari = models.TextField(blank=True, default='')
    notes_pashto = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['province', 'city']
        verbose_name_plural = "Coverage areas"

    def __str__(self):
        return f"{self.city}, {self.province} - {self.get_coverage_type_display()} ({self.get_status_display()})"


class TechnicalSupportFAQ(models.Model):
    CATEGORIES = [
        ('network', 'Network Issues'),
        ('device', 'Device Settings'),
        ('billing', 'Billing & Payments'),
        ('account', 'Account Management'),
        ('other', 'Other'),
    ]

    category = models.CharField(max_length=20, choices=CATEGORIES, default='other')
    question_en = models.TextField()
    question_dari = models.TextField(blank=True, default='')
    question_pashto = models.TextField(blank=True, default='')
    answer_en = models.TextField()
    answer_dari = models.TextField(blank=True, default='')
    answer_pashto = models.TextField(blank=True, default='')
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', 'question_en']
        verbose_name = "Technical Support FAQ"
        verbose_name_plural = "Technical Support FAQs"

    def __str__(self):
        return f"[{self.get_category_display()}] {self.question_en[:60]}"


class AppConfig(models.Model):
    """Store application configuration like API keys."""
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField(blank=True, default='')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "App Configuration"
        verbose_name_plural = "App Configurations"

    def __str__(self):
        return self.key
