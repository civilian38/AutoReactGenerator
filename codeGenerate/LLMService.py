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
        for apidoc in context_data.get('apidocs'):
            request_text += str(apidoc) + "\n"

    # discussions
    if context_data.get('discussions'):
        request_text += "====Discussions====\n"
        for discussion in context_data.get('discussions'):
            request_text += str(discussion) + "\n"

    # files
    if context_data.get('files'):
        request_text += "====Files====\n"
        for file in context_data.get('files'):
            request_text += str(file) + "\n"

    # pages
    if context_data.get('pages'):
        request_text += "====Pages====\n"
        for page in context_data.get('pages'):
            request_text += str(page) + "\n"

    return request_text