from google import genai
from pydantic import BaseModel, Field, create_model, AfterValidator, PlainSerializer
from enum import IntEnum
from typing import List, Annotated

from authentication.models import ARUser
from .models import GenerationSession, SessionChat
from .prompt import *


class FileToCreate(BaseModel):
    filename: str = Field(description="새로운 파일의 파일 명. 확장자까지 명시할 것.")
    filepath: str = Field(description="새로운 파일이 위치할 폴더의 이름. 기존 프로젝트에서 확인할 수 있는 루트폴더로부터 '/'로 하위 폴더를 구분하여 full path를 작성하되, 자체는 작성하지 말것.")
    content: str = Field(description="새로운 파일의 완성된 전체 코드")

def get_response_format_model(files_ids: List[int]):
    FileIdEnum = IntEnum('FileIdEnum', {f'ID_{item}': item for item in files_ids})
    RestrictedInt = Annotated[
        FileIdEnum, 
        AfterValidator(lambda x: x.value),
        PlainSerializer(lambda x: x, return_type=int)
    ]
    FileToModify = create_model(
        'FileToModify',
        file_id=(RestrictedInt, Field(description=f"수정할 파일의 id. 파일의 id는 파일 명 뒤에 | File ID: [] 로 적혀있다.")),
        modify_content=(str, Field(description="파일의 수정본. 수정본은 반드시 완성된 전체 코드로 되어 있어야 함."))
    )
    
    ResponseFormat = create_model(
        'ResponseFormat',
        files_to_modify=(List[FileToModify], Field(description="수정해야 할 파일들의 리스트")),
        files_to_create=(List[FileToCreate], Field(description="새롭게 추가할 파일들의 리스트")),
        response_text=(str, Field(description="요청자에게 전달할 구현 사항에 대한 설명")),
        handover_context=(str, Field(description="새롭게 작성할 handover context. 반드시 명시된 형식에 맞추어 작성할 것."))
    )
    return ResponseFormat

def get_generation_prompt(session_id):
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

def request_code_generation(session_id, user_id):
    user_obj = ARUser.objects.get(id=user_id)
    api_key = user_obj.gemini_key_encrypted
    client = genai.Client(api_key=api_key)

    current_session =  GenerationSession.objects.prefetch_related(
            'related_files',
        ).get(id=session_id)
    context_data = current_session.get_related_files()
    related_files_ids = [file.id for file in context_data.get('files')]

    ResponseFormat = get_response_format_model(related_files_ids)
    response = client.models.generate_content(
        model="gemini-3-pro-preview",
        contents=get_generation_prompt(session_id),
        config={
            "response_mime_type": "application/json",
            "response_json_schema": ResponseFormat.model_json_schema()
        }
    )

    generation_result = ResponseFormat.model_validate_json(response.text)
    return generation_result