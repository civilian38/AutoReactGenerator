from celery import shared_task

from .models import Discussion, DiscussionChat
from .serializers import DiscussionChatLLMSerializer, DiscussionSummarySerializer
from .LLMService import generate_chat_response, summarize_chats

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

@shared_task(bind=True)
def summarize_chat_and_save(self, discussion_id, user_id):
    discussion_object = Discussion.objects.get(id=discussion_id)
    response_text = summarize_chats(discussion_id, user_id)

    update_data = {'summary': response_text}
    serializer = DiscussionSummarySerializer(instance=discussion_object, data=update_data, partial=True)
    if not serializer.is_valid():
        raise ValueError(f"Validation Error: {serializer.errors}")

    serializer.save()
    return "SUCCESS"