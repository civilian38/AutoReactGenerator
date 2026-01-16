from google import genai
from google.genai.types import UserContent, ModelContent

from authentication.models import ARUser
from .models import GenerationSession, SessionChat
from .prompt import *

def prompt_test(session_id):
    current_session = GenerationSession.objects.prefetch_related(
            'related_apidocs',
            'related_discussions',
            'related_folders',
            'related_files',
            'related_pages'
        ).get(id=session_id)
    context_data = current_session.get_related_objects()
    session_project = current_session.project_under

    request_text = str()
    request_text += code_generate_init_message + "\n"

    # handover context
    request_text += "====Protocol: Handover Context====\n"
    request_text += handover_context_init_message + "\n"
    request_text += "현재까지 기록된 handover context는 다음과 같습니다.\n==========\n"
    request_text += session_project.handover_context + "\n==========\n"

    # apidocs
    if context_data.get('apidocs'):
        request_text += "====API DOCS====\n"
        request_text += apidoc_init_message + "\n"
        for apidoc in context_data.get('apidocs'):
            request_text += apidoc.get_prompt_text() + "\n"
    request_text += "\n"*2

    # discussions
    if context_data.get('discussions'):
        request_text += "====Discussions(기획서)====\n"
        request_text += discussion_init_message + "\n"
        for discussion in context_data.get('discussions'):
            request_text += discussion.get_prompt_text() + "\n"

    # files
    if context_data.get('files'):
        request_text += "====(기존 파일)====\n"
        request_text += file_init_message + "\n"
        for file in context_data.get('files'):
            request_text += file.get_prompt_text() + "\n"

    # pages
    if context_data.get('pages'):
        request_text += "====Pages====\n"
        request_text += page_init_message + "\n"
        for page in context_data.get('pages'):
            request_text += page.get_prompt_text() + "\n"
    
    # chats    
    Chats = SessionChat.objects.filter(session_under=current_session)
    if Chats.exists():
        request_text += "=====Chats====="
        request_text += request_init_message + "\n"
        for chat in Chats:
            request_text += f"({"USER" if chat.is_by_user else "AGENT"}) {chat.content}\n"

    request_text += "====Request====\n"
    request_text += code_generate_final_message
    

    return request_text