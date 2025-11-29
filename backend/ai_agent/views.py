# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.response import Response
# from rest_framework import status
# import logging
# import uuid

# from .models import Conversation, Message
# from .serializers import ChatRequestSerializer, VoiceChatRequestSerializer
# from .services.ai_service import TelecomAIService

# logger = logging.getLogger(__name__)
# ai_service = TelecomAIService()

# @api_view(['POST'])
# @permission_classes([])
# def chat_endpoint(request):
#     try:
#         serializer = ChatRequestSerializer(data=request.data)
#         if not serializer.is_valid():
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
#         data = serializer.validated_data
#         user_message = data['message']
#         session_id = data.get('session_id', str(uuid.uuid4()))
#         language = data['language']
        
#         conversation, created = Conversation.objects.get_or_create(
#             session_id=session_id,
#             defaults={'user_language': language}
#         )
        
#         if conversation.user_language != language:
#             conversation.user_language = language
#             conversation.save()
        
#         user_msg = Message.objects.create(
#             conversation=conversation,
#             content=user_message,
#             is_user=True
#         )
        
#         ai_response = ai_service.generate_response(user_message, language)
        
#         ai_msg = Message.objects.create(
#             conversation=conversation,
#             content=ai_response,
#             is_user=False
#         )
        
#         return Response({
#             'response': ai_response,
#             'session_id': session_id,
#             'message_id': str(ai_msg.id)
#         })
        
#     except Exception as e:
#         logger.error(f"Chat error: {e}")
#         return Response(
#             {'error': 'Internal server error'}, 
#             status=status.HTTP_500_INTERNAL_SERVER_ERROR
#         )

# @api_view(['POST'])
# @permission_classes([])
# def voice_chat_endpoint(request):
#     try:
#         serializer = VoiceChatRequestSerializer(data=request.data)
#         if not serializer.is_valid():
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
#         data = serializer.validated_data
#         session_id = data.get('session_id', str(uuid.uuid4()))
#         language = data['language']
#         transcribed_text = data.get('text', '')
        
#         if not transcribed_text:
#             return Response(
#                 {'error': 'No text provided'}, 
#                 status=status.HTTP_400_BAD_REQUEST
#             )
        
#         conversation, created = Conversation.objects.get_or_create(
#             session_id=session_id,
#             defaults={'user_language': language}
#         )
        
#         user_msg = Message.objects.create(
#             conversation=conversation,
#             content=transcribed_text,
#             is_user=True
#         )
        
#         ai_response = ai_service.generate_response(transcribed_text, language)
        
#         ai_msg = Message.objects.create(
#             conversation=conversation,
#             content=ai_response,
#             is_user=False
#         )
        
#         return Response({
#             'response': ai_response,
#             'session_id': session_id,
#             'original_text': transcribed_text
#         })
        
#     except Exception as e:
#         logger.error(f"Voice chat error: {e}")
#         return Response(
#             {'error': 'Voice processing error'}, 
#             status=status.HTTP_500_INTERNAL_SERVER_ERROR
#         )

# @api_view(['GET'])
# @permission_classes([])
# def health_check(request):
#     return Response({
#         'status': 'healthy',
#         'service': 'Telecom AI Agent API',
#         'version': '1.0.0'
#     })







from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
import logging
import uuid

from .models import Conversation, Message
from .serializers import ChatRequestSerializer, VoiceChatRequestSerializer

logger = logging.getLogger(__name__)

# Always use Mock Service to avoid API key issues
try:
    from .services.mock_ai_service import MockAIService
    ai_service = MockAIService()
    AI_SERVICE_AVAILABLE = True
    logger.info("✅ Using Mock AI Service - No API key required")
except Exception as e:
    logger.error(f"❌ Failed to initialize Mock AI Service: {e}")
    ai_service = None
    AI_SERVICE_AVAILABLE = False

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
        
        logger.info(f"💬 Processing chat request - Session: {session_id}, Language: {language}, Message: {user_message}")
        
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
        
        # Generate AI response using Mock service
        ai_response = ai_service.generate_response(user_message, language)
        
        # Save AI response
        ai_msg = Message.objects.create(
            conversation=conversation,
            content=ai_response,
            is_user=False
        )
        
        logger.info(f"🤖 AI Response generated: {ai_response[:100]}...")
        
        return Response({
            'response': ai_response,
            'session_id': session_id,
            'message_id': str(ai_msg.id),
            'status': 'success',
            'ai_provider': 'mock'  # Indicate we're using mock service
        })
        
    except Exception as e:
        logger.error(f"💥 Chat endpoint error: {e}")
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
        logger.error(f"💥 Voice chat endpoint error: {e}")
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
            # Test with a simple message
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
            'version': '1.0.0',
            'message': 'Mock AI service is providing realistic telecom responses'
        })
    except Exception as e:
        return Response({
            'status': 'degraded',
            'service': 'Telecom AI Agent API', 
            'ai_service': 'unavailable',
            'error': str(e),
            'version': '1.0.0'
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)