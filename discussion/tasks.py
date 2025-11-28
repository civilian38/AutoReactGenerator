from celery import shared_task
from .serializers import DiscussionChatLLMSerializer
from .LLMService import generate_chat_response

@shared_task(bind=True)
def get_chat_response_and_save(self, user_message, discussion_id, user_id):
    response_text = generate_chat_response(user_message, discussion_id, user_id)

    response_data = {
        'discussion_under': discussion_id,
        'content': response_text,
        'is_by_user': False
    }
    llm_response_serializer = DiscussionChatLLMSerializer(data=response_data)

    if not llm_response_serializer.is_valid():
        raise ValueError(f"Validation Error: {llm_response_serializer.errors}")

    llm_response_serializer.save()
    return "SUCCESS"