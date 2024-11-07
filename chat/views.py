from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import ChatMessage
from .serializers import ChatMessageSerializer
import g4f

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat_response(request):
    message = request.data.get('message')
    
    if not message:
        return Response(
            {'error': 'Message is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Get response from g4f
        response = g4f.ChatCompletion.create(
            model=g4f.models.gpt_35_turbo,
            messages=[
                {"role": "system", "content": "You are a helpful learning assistant focused on education and academic support."},
                {"role": "user", "content": message}
            ],
            stream=False
        )

        # Save the chat message and response
        chat_message = ChatMessage.objects.create(
            user=request.user,
            message=message,
            response=response
        )

        serializer = ChatMessageSerializer(chat_message)
        return Response(serializer.data)

    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_chat_history(request):
    chat_messages = ChatMessage.objects.filter(user=request.user)
    serializer = ChatMessageSerializer(chat_messages, many=True)
    return Response(serializer.data)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def clear_chat_history(request):
    ChatMessage.objects.filter(user=request.user).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
