from .models import Discussion, DiscussionChat
from .serializers import DiscussionChatLLMSerializer, DiscussionSummarySerializer
from .LLMService import generate_chat_response, summarize_chats, generate_short_summary

import logging
from django.db import transaction
from celery import shared_task

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def get_chat_response_and_save(self, discussion_id, user_id, last_chat_id):
    try:
        response_text = generate_chat_response(discussion_id, user_id)

        with transaction.atomic():
            discussion = Discussion.objects.select_for_update().get(id=discussion_id)

            response_data = {
                'discussion_under': discussion_id,
                'content': response_text,
                'is_by_user': False
            }
            llm_response_serializer = DiscussionChatLLMSerializer(data=response_data)

            if not llm_response_serializer.is_valid():
                raise ValueError(f"Serializer Validation Error: {llm_response_serializer.errors}")

            llm_response_serializer.save()

            discussion.is_occupied = False
            discussion.save()

            return "SUCCESS"

    except Exception as e:
        logger.error(f"Celery Task Failed (Discussion ID: {discussion_id}): {e}", exc_info=True)

        try:
            with transaction.atomic():
                discussion = Discussion.objects.select_for_update().get(id=discussion_id)
                discussion.is_occupied = False
                discussion.save()

                DiscussionChat.objects.filter(id=last_chat_id).delete()

        except Exception as cleanup_error:
            logger.critical(f"Critical: Failed to cleanup discussion state: {cleanup_error}")

        raise e

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

@shared_task(bind=True)
def make_short_summary_task(self, discussion_id, user_id):
    discussion_object = Discussion.objects.get(id=discussion_id)
    response_text = generate_short_summary(discussion_id, user_id)

    update_data = {'short_summary': response_text}
    serializer = DiscussionSummarySerializer(instance=discussion_object, data=update_data, partial=True)
    if not serializer.is_valid():
        raise ValueError(f"Validation Error: {serializer.errors}")

    serializer.save()
    return "SUCCESS"
