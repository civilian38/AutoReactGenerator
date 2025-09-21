from google import genai
from google.genai.errors import ClientError, ServerError
from google.genai.types import UserContent, ModelContent
from rest_framework import status
from rest_framework.response import Response

from AutoReactGenerator.prompt import discussion_chat_init_message, discussion_chat_request_message
from authentication.models import ARUser
from .models import *

def generate_response(user_message, discussion_id, user_id):
    current_discussion = Discussion.objects.get(id=discussion_id)
    prev_chats = DiscussionChat.objects.filter(discussion_under=current_discussion)

    history = list()
    history.append(UserContent(discussion_chat_init_message))
    for chat in prev_chats:
        if chat.is_by_user:
            history.append(UserContent(chat.content))
        else:
            history.append(ModelContent(chat.content))
    history.append(UserContent(discussion_chat_request_message))

    user_obj = ARUser.objects.get(id=user_id)
    api_key = user_obj.gemini_key_encrypted

    try:
        client = genai.Client(api_key=api_key)
        chat_generator = client.chats.create(model="gemini-2.5-pro", history=history)
        response = chat_generator.send_message(user_message)
        return response.text
    except ClientError as e:
        return Response(
            {
                "type": "ClientError",
                "message": e.message,
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    except ServerError as e:
        return Response(
            {
                "type": "ServerError",
                "message": e.message,
            },
            status=status.HTTP_502_BAD_GATEWAY
        )
    except Exception as e:
        return Response(
            {
                "type": "UnexpectedError",
                "message": e.message,
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )