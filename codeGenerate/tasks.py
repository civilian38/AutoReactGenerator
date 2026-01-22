from .models import GenerationSession, SessionChat
from .LLMService import request_code_generation

from frontFile.models import ProjectFile, Folder

import logging
from django.db import transaction
from celery import shared_task

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def request_generate_and_apply(self, session_id, user_id, last_chat_id):
    try:
        response_result = request_code_generation(session_id, user_id)
        session = GenerationSession.objects.get(id=session_id)
        project = session.project_under
        file_root_folder = Folder.objects.filter(
            project_under=project,  
            parent_folder__isnull=True    
        ).first()

        with transaction.atomic():
            # modify existing files
            for modification_data in response_result.files_to_modify:
                target_file = ProjectFile.objects.get(id=modification_data.file_id)
                target_file.draft_content = modification_data.modify_content
                target_file.save()
            
            # create new files
            for creation_data in response_result.files_to_create:
                folder_under = file_root_folder.get_or_create_by_path(creation_data.filepath)
                ProjectFile.objects.create(
                    project_under=project,
                    folder=folder_under,
                    name=creation_data.filename,
                    content=None,
                    draft_content=creation_data.content
                )
            
            # update handover context
            project.handover_context = response_result.handover_context

            # update to do request if exists
            if response_result.to_do_request:
                project.to_do_request = response_result.to_do_request
            project.save()

            # reply to user message
            SessionChat.objects.create(
                session_under=session,
                content=response_result.response_text,
                is_by_user=False
            )

            # unoccupy
            session.is_occupied = False
            session.save()

            return "SUCCESS"
                
    except Exception as e:
        logger.error(f"Celery Task Failed (Session ID: {session_id}): {e}", exc_info=True)

        try:
            with transaction.atomic():
                session = GenerationSession.objects.select_for_update(id=session_id)
                session.is_occupied = False
                session.save()

                SessionChat.objects.filter(id=last_chat_id).delete()

        except Exception as cleanup_error:
            logger.critical(f"Critical: Failed to cleanup discussion state: {cleanup_error}")

        raise e
