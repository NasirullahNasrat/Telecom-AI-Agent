import requests
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
import logging
import uuid

from .models import (
    Conversation, Message, TelecomKnowledgeBase,
    InternetPackage, CoverageArea, TechnicalSupportFAQ,
    AppConfig
)
from .serializers import (
    ChatRequestSerializer, VoiceChatRequestSerializer,
    TelecomKnowledgeBaseSerializer, InternetPackageSerializer,
    CoverageAreaSerializer, TechnicalSupportFAQSerializer,
    AppConfigSerializer
)

logger = logging.getLogger(__name__)

SENSITIVE_KEYS = ('deepseek_api_key', 'openai_api_key')


def _cleanup_masked_keys():
    """Remove any masked API key values that may have been stored by older code."""
    try:
        for key in SENSITIVE_KEYS:
            cfg = AppConfig.objects.filter(key=key).first()
            if cfg and cfg.value and '*' in cfg.value:
                logger.warning(f"Removing masked value for {key} (stored by old code)")
                cfg.delete()
    except Exception:
        pass


# Clean up any masked values stored by old code
_cleanup_masked_keys()

# Try to use the real DeepSeek AI service first, fall back to Mock service
try:
    from django.conf import settings
    from .services.ai_service import TelecomAIService
    if settings.DEEPSEEK_API_KEY and settings.DEEPSEEK_API_KEY != 'your-deepseek-api-key-here':
        ai_service = TelecomAIService()
        AI_SERVICE_AVAILABLE = True
        AI_PROVIDER = 'deepseek'
        logger.info("Using DeepSeek AI Service - Real AI responses enabled")
    else:
        raise ValueError("No valid API key configured")
except Exception:
    try:
        from .services.mock_ai_service import MockAIService
        ai_service = MockAIService()
        AI_SERVICE_AVAILABLE = True
        AI_PROVIDER = 'mock'
        logger.info("Using Mock AI Service - No API key required")
    except Exception as e:
        logger.error(f"Failed to initialize Mock AI Service: {e}")
        ai_service = None
        AI_SERVICE_AVAILABLE = False
        AI_PROVIDER = 'none'


# ============================================================
# Chat & Voice Endpoints
# ============================================================

@api_view(['POST'])
@permission_classes([])
def chat_endpoint(request):
    try:
        if not AI_SERVICE_AVAILABLE:
            return Response({
                'error': 'AI service is currently unavailable. Please check configuration.'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        serializer = ChatRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        user_message = data['message']
        session_id = data.get('session_id', str(uuid.uuid4()))
        language = data['language']

        logger.info(f"Processing chat request - Session: {session_id}, Language: {language}, Message: {user_message}")

        conversation, created = Conversation.objects.get_or_create(
            session_id=session_id,
            defaults={'user_language': language}
        )

        if conversation.user_language != language:
            conversation.user_language = language
            conversation.save()

        # Save user message
        user_msg = Message.objects.create(
            conversation=conversation,
            content=user_message,
            is_user=True
        )

        # Generate AI response - use RAG context for DeepSeek, or let Mock handle it
        if AI_PROVIDER == 'deepseek':
            # Get RAG context to feed into DeepSeek for natural responses
            from .services.rag_service import RAGService
            rag = RAGService()
            rag_context = rag.retrieve_context(user_message, language, top_k=3)
            ai_response = ai_service.generate_response(user_message, language, rag_context=rag_context)
        else:
            # Mock service handles RAG internally
            ai_response = ai_service.generate_response(user_message, language)

        # Save AI response
        ai_msg = Message.objects.create(
            conversation=conversation,
            content=ai_response,
            is_user=False
        )

        logger.info(f"AI Response generated: {ai_response[:100]}...")

        return Response({
            'response': ai_response,
            'session_id': session_id,
            'message_id': str(ai_msg.id),
            'status': 'success',
            'ai_provider': AI_PROVIDER
        })

    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        return Response({
            'error': 'Internal server error',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([])
def voice_chat_endpoint(request):
    try:
        if not AI_SERVICE_AVAILABLE:
            return Response({
                'error': 'AI service is currently unavailable'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        serializer = VoiceChatRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        session_id = data.get('session_id', str(uuid.uuid4()))
        language = data['language']
        transcribed_text = data.get('text', '')

        if not transcribed_text:
            return Response(
                {'error': 'No text provided for voice processing'},
                status=status.HTTP_400_BAD_REQUEST
            )

        conversation, created = Conversation.objects.get_or_create(
            session_id=session_id,
            defaults={'user_language': language}
        )

        user_msg = Message.objects.create(
            conversation=conversation,
            content=transcribed_text,
            is_user=True
        )

        ai_response = ai_service.generate_response(transcribed_text, language)

        ai_msg = Message.objects.create(
            conversation=conversation,
            content=ai_response,
            is_user=False
        )

        return Response({
            'response': ai_response,
            'session_id': session_id,
            'original_text': transcribed_text,
            'status': 'success',
            'ai_provider': 'mock'
        })

    except Exception as e:
        logger.error(f"Voice chat endpoint error: {e}")
        return Response(
            {'error': 'Voice processing error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([])
def health_check(request):
    """Health check endpoint"""
    try:
        if AI_SERVICE_AVAILABLE:
            test_response = ai_service.generate_response("Hello", "en")
            ai_status = "healthy"
            ai_provider = "mock"
        else:
            ai_status = "unavailable"
            ai_provider = "none"

        return Response({
            'status': 'healthy',
            'service': 'Telecom AI Agent API',
            'ai_service': ai_status,
            'ai_provider': ai_provider,
            'version': '1.1.0',
            'message': 'RAG-powered AI service retrieving real data from database'
        })
    except Exception as e:
        return Response({
            'status': 'degraded',
            'service': 'Telecom AI Agent API',
            'ai_service': 'unavailable',
            'error': str(e),
            'version': '1.1.0'
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)


# ============================================================
# Admin Login Endpoint
# ============================================================

@api_view(['POST'])
@permission_classes([AllowAny])
def admin_login(request):
    """Authenticate admin user and return a token."""
    username = request.data.get('username', '')
    password = request.data.get('password', '')
    user = authenticate(username=username, password=password)
    if user:
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'username': user.username,
            'is_staff': user.is_staff,
        })
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


# ============================================================
# Admin CRUD API Endpoints (Authentication Required)
# ============================================================

# --- TelecomKnowledgeBase CRUD ---

@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def knowledge_base_list(request):
    """List all or create a new knowledge base entry."""
    if request.method == 'GET':
        entries = TelecomKnowledgeBase.objects.all().order_by('-created_at')
        serializer = TelecomKnowledgeBaseSerializer(entries, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = TelecomKnowledgeBaseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Created KnowledgeBase entry: {serializer.data.get('question_en', '')[:50]}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def knowledge_base_detail(request, pk):
    """Retrieve, update or delete a knowledge base entry."""
    try:
        entry = TelecomKnowledgeBase.objects.get(pk=pk)
    except TelecomKnowledgeBase.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = TelecomKnowledgeBaseSerializer(entry)
        return Response(serializer.data)

    elif request.method in ('PUT', 'PATCH'):
        partial = request.method == 'PATCH'
        serializer = TelecomKnowledgeBaseSerializer(entry, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        entry.delete()
        logger.info(f"Deleted KnowledgeBase entry {pk}")
        return Response(status=status.HTTP_204_NO_CONTENT)


# --- InternetPackage CRUD ---

@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def internet_package_list(request):
    """List all or create a new internet package."""
    if request.method == 'GET':
        packages = InternetPackage.objects.all().order_by('price_afn')
        serializer = InternetPackageSerializer(packages, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = InternetPackageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Created InternetPackage: {serializer.data.get('name_en', '')}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def internet_package_detail(request, pk):
    """Retrieve, update or delete an internet package."""
    try:
        pkg = InternetPackage.objects.get(pk=pk)
    except InternetPackage.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = InternetPackageSerializer(pkg)
        return Response(serializer.data)

    elif request.method in ('PUT', 'PATCH'):
        partial = request.method == 'PATCH'
        serializer = InternetPackageSerializer(pkg, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        pkg.delete()
        logger.info(f"Deleted InternetPackage {pk}")
        return Response(status=status.HTTP_204_NO_CONTENT)


# --- CoverageArea CRUD ---

@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def coverage_area_list(request):
    """List all or create a new coverage area."""
    if request.method == 'GET':
        areas = CoverageArea.objects.all().order_by('province', 'city')
        serializer = CoverageAreaSerializer(areas, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = CoverageAreaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Created CoverageArea: {serializer.data.get('city', '')}, {serializer.data.get('province', '')}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def coverage_area_detail(request, pk):
    """Retrieve, update or delete a coverage area."""
    try:
        area = CoverageArea.objects.get(pk=pk)
    except CoverageArea.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = CoverageAreaSerializer(area)
        return Response(serializer.data)

    elif request.method in ('PUT', 'PATCH'):
        partial = request.method == 'PATCH'
        serializer = CoverageAreaSerializer(area, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        area.delete()
        logger.info(f"Deleted CoverageArea {pk}")
        return Response(status=status.HTTP_204_NO_CONTENT)


# --- TechnicalSupportFAQ CRUD ---

@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def faq_list(request):
    """List all or create a new FAQ."""
    if request.method == 'GET':
        faqs = TechnicalSupportFAQ.objects.all().order_by('category', 'question_en')
        serializer = TechnicalSupportFAQSerializer(faqs, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = TechnicalSupportFAQSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Created FAQ: {serializer.data.get('question_en', '')[:50]}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def faq_detail(request, pk):
    """Retrieve, update or delete a FAQ."""
    try:
        faq = TechnicalSupportFAQ.objects.get(pk=pk)
    except TechnicalSupportFAQ.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = TechnicalSupportFAQSerializer(faq)
        return Response(serializer.data)

    elif request.method in ('PUT', 'PATCH'):
        partial = request.method == 'PATCH'
        serializer = TechnicalSupportFAQSerializer(faq, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        faq.delete()
        logger.info(f"Deleted FAQ {pk}")
        return Response(status=status.HTTP_204_NO_CONTENT)


# --- Dashboard Stats ---

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def admin_stats(request):
    """Get dashboard statistics for the admin panel."""
    try:
        stats = {
            'total_conversations': Conversation.objects.count(),
            'total_messages': Message.objects.count(),
            'total_kb_entries': TelecomKnowledgeBase.objects.count(),
            'total_packages': InternetPackage.objects.count(),
            'active_packages': InternetPackage.objects.filter(is_active=True).count(),
            'total_coverage_areas': CoverageArea.objects.count(),
            'active_coverage_areas': CoverageArea.objects.filter(status='active').count(),
            'total_faqs': TechnicalSupportFAQ.objects.count(),
            'published_faqs': TechnicalSupportFAQ.objects.filter(is_published=True).count(),
        }
        return Response(stats)
    except Exception as e:
        logger.error(f"Admin stats error: {e}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================================
# Admin Settings (API Key Configuration)
# ============================================================

def _reinitialize_ai_service():
    """Reinitialize the global ai_service based on current AppConfig settings."""
    global ai_service, AI_SERVICE_AVAILABLE, AI_PROVIDER

    try:
        # Read config from database
        provider = AppConfig.objects.filter(key='ai_provider').first()
        deepseek_key = AppConfig.objects.filter(key='deepseek_api_key').first()
        openai_key = AppConfig.objects.filter(key='openai_api_key').first()

        provider_value = provider.value if provider else 'mock'
        deepseek_value = deepseek_key.value if deepseek_key else ''
        openai_value = openai_key.value if openai_key else ''

        # Safety: treat masked values (containing asterisks) as empty
        if '*' in deepseek_value:
            logger.warning("DeepSeek API key contains masked characters — treating as empty")
            deepseek_value = ''
        if '*' in openai_value:
            logger.warning("OpenAI API key contains masked characters — treating as empty")
            openai_value = ''

        from django.conf import settings

        if provider_value == 'deepseek' and deepseek_value:
            # Initialize DeepSeek via TelecomAIService
            from .services.ai_service import TelecomAIService
            # Persist the key to settings so TelecomAIService can read it
            settings.DEEPSEEK_API_KEY = deepseek_value
            ai_service = TelecomAIService()
            AI_SERVICE_AVAILABLE = True
            AI_PROVIDER = 'deepseek'
            logger.info(f"AI Service reinitialized to DeepSeek with key from settings")
        elif provider_value == 'openai' and openai_value:
            # Use the dedicated OpenAIService
            from .services.openai_service import OpenAIService
            # Persist the key to settings so OpenAIService can read it
            settings.OPENAI_API_KEY = openai_value
            ai_service = OpenAIService()
            AI_SERVICE_AVAILABLE = True
            AI_PROVIDER = 'openai'
            logger.info(f"AI Service reinitialized to OpenAI with key from settings")
        else:
            # Fall back to Mock service
            from .services.mock_ai_service import MockAIService
            ai_service = MockAIService()
            AI_SERVICE_AVAILABLE = True
            AI_PROVIDER = 'mock'
            logger.info("AI Service reinitialized to Mock (no valid API key)")

        return True
    except Exception as e:
        logger.error(f"Failed to reinitialize AI service: {e}")
        # Fall back to Mock
        try:
            from .services.mock_ai_service import MockAIService
            ai_service = MockAIService()
            AI_SERVICE_AVAILABLE = True
            AI_PROVIDER = 'mock'
        except Exception:
            ai_service = None
            AI_SERVICE_AVAILABLE = False
            AI_PROVIDER = 'none'
        return False


@api_view(['GET', 'POST', 'DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def admin_settings(request):
    """Get or update application settings (API keys, provider selection)."""
    if request.method == 'GET':
        # Return all config values (masked for security on sensitive keys)
        configs = AppConfig.objects.all()
        data = {}
        for cfg in configs:
            if cfg.key in SENSITIVE_KEYS:
                # Mask the value for security - show only last 4 chars
                val = cfg.value
                if val and len(val) > 8:
                    data[cfg.key] = val[:4] + '*' * (len(val) - 8) + val[-4:]
                elif val:
                    data[cfg.key] = '*' * len(val)
                else:
                    data[cfg.key] = ''
            else:
                data[cfg.key] = cfg.value
        return Response(data)

    elif request.method == 'POST':
        key = request.data.get('key', '')
        value = request.data.get('value', '')

        if not key:
            return Response({'error': 'Key is required'}, status=status.HTTP_400_BAD_REQUEST)

        # If the value looks like a masked key (contains asterisks), reject the update
        # to prevent accidentally saving masked data back
        if key in SENSITIVE_KEYS and value and '*' in value:
            return Response({
                'error': 'Cannot save masked value. Please enter the actual API key or leave empty to clear it.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Save to database
        config, created = AppConfig.objects.update_or_create(
            key=key,
            defaults={'value': value}
        )

        # If the key being updated is ai_provider, deepseek_api_key, or openai_api_key,
        # reinitialize the AI service
        if key in ('ai_provider', 'deepseek_api_key', 'openai_api_key'):
            success = _reinitialize_ai_service()
            if success:
                logger.info(f"AI service reinitialized after config change: {key}")
            else:
                logger.warning(f"AI service reinitialization failed after config change: {key}")

        return Response({
            'key': config.key,
            'value': config.value,
            'updated_at': config.updated_at,
            'ai_provider': AI_PROVIDER,
            'ai_service_available': AI_SERVICE_AVAILABLE,
        }, status=status.HTTP_200_OK)

    elif request.method == 'DELETE':
        key = request.data.get('key', '')
        if not key:
            return Response({'error': 'Key is required'}, status=status.HTTP_400_BAD_REQUEST)

        deleted, _ = AppConfig.objects.filter(key=key).delete()
        if deleted:
            logger.info(f"Deleted config key: {key}")
            # Reinitialize if a provider key was deleted
            if key in ('ai_provider', 'deepseek_api_key', 'openai_api_key'):
                _reinitialize_ai_service()
            return Response({'message': f'Config key "{key}" deleted'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': f'Config key "{key}" not found'}, status=status.HTTP_404_NOT_FOUND)


# ============================================================
# Text-to-Speech Endpoints (API-based TTS for Dari/Pashto)
# ============================================================

@api_view(['GET'])
@permission_classes([])
def tts_status(request):
    """Check if API-based TTS is available (requires OpenAI or DeepSeek key)."""
    openai_key = ''
    deepseek_key = ''
    try:
        openai_cfg = AppConfig.objects.filter(key='openai_api_key').first()
        deepseek_cfg = AppConfig.objects.filter(key='deepseek_api_key').first()
        if openai_cfg:
            openai_key = openai_cfg.value
        if deepseek_cfg:
            deepseek_key = deepseek_cfg.value
    except Exception:
        pass

    # Also check settings (use getattr for safety since OPENAI_API_KEY may not be defined)
    from django.conf import settings
    settings_openai = getattr(settings, 'OPENAI_API_KEY', '')
    if not openai_key and settings_openai and settings_openai != 'your-openai-api-key-here':
        openai_key = settings_openai
    if not deepseek_key and settings.DEEPSEEK_API_KEY and settings.DEEPSEEK_API_KEY != 'your-deepseek-api-key-here':
        deepseek_key = settings.DEEPSEEK_API_KEY

    # OpenAI TTS is preferred (has proper multi-language support)
    # DeepSeek doesn't have a TTS API, so only OpenAI works for API TTS
    available = bool(openai_key) and openai_key != 'your-openai-api-key-here'
    provider = 'openai' if available else ('deepseek' if deepseek_key else 'none')

    return Response({
        'available': available,
        'provider': provider,
    })


@api_view(['POST'])
@permission_classes([])
def tts_speak(request):
    """Generate speech audio using OpenAI TTS API."""
    text = request.data.get('text', '')
    language = request.data.get('language', 'en')

    if not text:
        return Response({'error': 'Text is required'}, status=status.HTTP_400_BAD_REQUEST)

    # Get the OpenAI API key
    openai_key = ''
    try:
        openai_cfg = AppConfig.objects.filter(key='openai_api_key').first()
        if openai_cfg:
            openai_key = openai_cfg.value
    except Exception:
        pass

    from django.conf import settings
    if not openai_key:
        openai_key = getattr(settings, 'OPENAI_API_KEY', '')

    if not openai_key or openai_key == 'your-openai-api-key-here':
        return Response(
            {'error': 'OpenAI API key not configured. Please add it in Admin Settings.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Map language to OpenAI voice
    # OpenAI TTS supports: alloy, echo, fable, onyx, nova, shimmer
    # For non-English, 'nova' and 'shimmer' tend to work better
    voice_map = {
        'en': 'nova',
        'fa': 'alloy',   # alloy works well for Persian/Dari
        'ps': 'alloy',   # alloy for Pashto too
    }
    voice = voice_map.get(language, 'alloy')

    # Map language to OpenAI TTS model language hint
    # OpenAI TTS supports: 'en', 'ja', 'zh', 'ko', 'de', 'fr', 'it', 'pt', 'pl', 'tr', 'ru', 'nl', 'ar', 'sv', 'fi', 'da', 'nb', 'cs', 'hu', 'ro', 'el', 'he', 'hi', 'th', 'id', 'ms', 'vi', 'bn', 'ta', 'te', 'mr', 'ur', 'pa', 'gu', 'kn', 'ml', 'si', 'ne', 'ps', 'fa'
    lang_map = {
        'en': 'en',
        'fa': 'fa',      # Persian/Farsi/Dari
        'ps': 'ps',      # Pashto
    }
    tts_lang = lang_map.get(language, 'en')

    try:
        headers = {
            "Authorization": f"Bearer {openai_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "tts-1",
            "input": text,
            "voice": voice,
            "response_format": "mp3",
            "speed": 1.0,
        }

        logger.info(f"TTS request: language={language}, voice={voice}, text length={len(text)}")

        response = requests.post(
            "https://api.openai.com/v1/audio/speech",
            headers=headers,
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            logger.info(f"TTS success: generated {len(response.content)} bytes of audio")
            from django.http import HttpResponse
            return HttpResponse(
                response.content,
                content_type='audio/mpeg',
                status=200
            )
        else:
            logger.error(f"OpenAI TTS API error: {response.status_code} - {response.text}")
            return Response(
                {'error': f'TTS API error: {response.status_code}'},
                status=status.HTTP_502_BAD_GATEWAY
            )

    except requests.exceptions.Timeout:
        logger.error("OpenAI TTS API request timed out")
        return Response({'error': 'TTS API request timed out'}, status=status.HTTP_504_GATEWAY_TIMEOUT)
    except requests.exceptions.RequestException as e:
        logger.error(f"OpenAI TTS API request failed: {e}")
        return Response({'error': str(e)}, status=status.HTTP_502_BAD_GATEWAY)
    except Exception as e:
        logger.error(f"Unexpected error in TTS: {e}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
