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

    request_text = str()
    request_text += code_generate_init_message + "\n"

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
    
    request_text += "====Request====\n"
    request_text += "위 정보를 종합하여 즉시 배포 가능한 수준의 코드를 작성하세요."

    return request_text