from google import genai
from google.genai import types
from pydantic import BaseModel, Field, create_model, AfterValidator, PlainSerializer
from enum import IntEnum, Enum
from typing import List, Annotated, Optional
from celery.utils.log import get_task_logger

from authentication.models import ARUser
from frontFile.models import Folder, ProjectFile
from .models import GenerationSession, SessionChat
from .prompt import *
from .helper import get_root_folder_with_prefetch_related

logger = get_task_logger(__name__)

def get_folder_to_create_list_model(project_name: str):
    FolderToCreate = create_model(
        'FolderToCreate',
        folderpath=(str, Field(
            description=(
                f"생성할 폴더의 전체 경로. "
                f"주의: './'나 '/'로 시작하지 말고, '{project_name}'와 같은 최상위 루트 폴더명부터 시작하여 전체 경로를 기입할 것. "
                f"(예시: '{project_name}/src/components/buttons')"
            )
        )),
        description=(str, Field(description="폴더에 대한 설명. 1~2문장 이내로 작성할것"))
    )

    ListFormat = create_model(
        'ListFormat',
        is_folder_creation_required=(bool, Field(
            description="새로 생성해야 할 폴더가 하나라도 존재하면 True, 기존 구조로 충분하면 False."
        )),
        folders_to_create=(List[FolderToCreate], Field(
            description="생성해야 할 폴더 객체들의 목록. 생성할 폴더가 없다면 빈 리스트를 반환."
        ))
    )
    return ListFormat

def get_response_format_model(files_ids: List[int], folders_ids: List[int]):
    FileIdEnum = IntEnum('FileIdEnum', {f'ID_{item}': item for item in files_ids})
    FileRestrictedInt = Annotated[
        FileIdEnum, 
        AfterValidator(lambda x: x.value),
        PlainSerializer(lambda x: x, return_type=int)
    ]
    FileToModify = create_model(
        'FileToModify', 
        file_id=(FileRestrictedInt, Field(description=f"수정할 파일의 id. 파일의 id는 파일 명 뒤에 | File ID: [] 로 적혀있다.")),
        modify_content=(str, Field(description="파일의 수정본. 수정본은 반드시 완성된 전체 코드로 되어 있어야 함.")),
        description=(str, Field(description="다음 코드 생성 에이전트가 자신이 구현하고 있는 사항에 이 코드가 필요한지 판단하기 위해 참고할 설명. 1~2문장 이내로 작성할 것."))
    )

    FolderIdEnum = IntEnum('FolderIdEnum', {f'ID_{item}': item for item in folders_ids})
    FolderRestrictedInt = Annotated[
        FolderIdEnum, 
        AfterValidator(lambda x: x.value),
        PlainSerializer(lambda x: x, return_type=int)
    ]
    FileToCreate = create_model(
        'FileToCreate',
        folder_id=(FolderRestrictedInt, Field(description="새롭게 만들 파일이 위치할 폴더의 id. 폴더의 id는 폴더 목록에서 폴더 경로 앞에 [0] 과 같이 적혀 있다.")),
        filename=(str,Field(description="새로운 파일의 파일 명. 확장자까지 명시할 것.")),
        content=(str, Field(description="새로운 파일의 완성된 전체 코드")),
        description=(str, Field(description="다음 코드 생성 에이전트가 자신이 구현하고 있는 사항에 이 코드가 필요한지 판단하기 위해 참고할 설명. 1~2문장 이내로 작성할 것."))
    )

    ResponseFormat = create_model(
        'ResponseFormat',
        files_to_modify=(List[FileToModify], Field(description="수정해야 할 파일들의 리스트")),
        files_to_create=(List[FileToCreate], Field(description="새롭게 추가할 파일들의 리스트")),
        response_text=(str, Field(description="요청자에게 전달할 구현 사항에 대한 설명")),
        handover_context=(str, Field(description="새롭게 작성할 handover context. 반드시 명시된 형식에 맞추어 작성할 것.")),
        to_do_request=(Optional[str], Field(default=None, description="새로운 패키지 설치, 환경변수 추가 등 코드 수정에 앞서 사용자가 필수적으로 취해야 할 행동"))
    )
    return ResponseFormat

def get_folder_generation_prompt(session_id) -> str:
    """
    generation 1단계: 폴더 생성을 위한 프롬프트 작성
    
    :param session_id: 요청이 들어온 session의 id
    """
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
    request_text += folder_generate_init_message + "\n"

    # handover context
    request_text += "====Handover Context====\n"
    request_text += folder_handover_context_init_message + "\n"
    request_text += session_project.get_prompt_text() + "\n"
    request_text += "=" * 8 + "\n"

    # folder structure
    all_folders = Folder.objects.filter(project_under=session_project).select_related('parent_folder')
    folder_dict = {folder.id: folder for folder in all_folders}
    root_folder = get_root_folder_with_prefetch_related(all_folders, folder_dict)
    
    request_text += "====Folder Structure====\n"
    request_text += folder_structure_init_message + "\n"
    request_text += root_folder.get_tree_structure() + "\n"
    request_text += "=" * 8 + "\n"

    # files
    if context_data.get('files'):
        request_text += "====(기존 파일)====\n"
        request_text += folder_file_init_message + "\n"
        for file in context_data.get('files'):
            request_text += "- " + file.name + "\n"

    # discussions
    if context_data.get('discussions'):
        request_text += "====Discussions(기획서)====\n"
        request_text += folder_discussion_init_message + "\n"
        for discussion in context_data.get('discussions'):
            request_text += discussion.get_prompt_text(short_version=True) + "\n"
    
    # pages
    if context_data.get('pages'):
        request_text += "====Pages====\n"
        request_text += folder_page_init_message + "\n"
        for page in context_data.get('pages'):
            request_text += page.get_prompt_text() + "\n"
    
    # apidocs
    if context_data.get('apidocs'):
        request_text += "====API DOCS====\n"
        request_text += folder_apidoc_init_message + "\n"
        for apidoc in context_data.get('apidocs'):
            request_text += apidoc.get_prompt_text() + "\n"
    request_text += "\n"*2

    # chats    
    Chats = SessionChat.objects.filter(session_under=current_session)
    if Chats.exists():
        request_text += "=====Chats====="
        request_text += request_init_message + "\n"
        for chat in Chats:
            request_text += f"({'USER' if chat.is_by_user else 'AGENT'}) {chat.content}\n"
    
    request_text += "\n" * 3
    request_text += folder_generate_final_message
    
    return request_text
   
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
    request_text += "====Project Outline====\n"
    request_text += project_outline_init_message + "\n"
    request_text += session_project.instruction + "\n"

    # handover context
    request_text += "====Protocol: Handover Context====\n"
    request_text += handover_context_init_message + "\n"
    request_text += "현재까지 기록된 handover context는 다음과 같습니다.\n==========\n"
    request_text += session_project.get_prompt_text() + "\n==========\n"

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

    # folder structure
    all_folders = Folder.objects.filter(project_under=session_project).select_related('parent_folder')
    folder_dict = {folder.id: folder for folder in all_folders}
    root_folder = get_root_folder_with_prefetch_related(all_folders, folder_dict)
    
    request_text += "====Folder Structure====\n"
    request_text += structure_init_message + "\n"
    request_text += root_folder.get_tree_structure() + "\n"
    request_text += "=" * 8 + "\n"

    # related files
    if context_data.get('files'):
        request_text += "====(기존 파일)====\n"
        request_text += file_init_message + "\n"
        for file in context_data.get('files'):
            request_text += file.get_prompt_text() + "\n"

    # entire file list
    all_files = ProjectFile.objects.filter(project_under=session_project).all()
    request_text += "====File List====\n"
    request_text += file_list_init_message + "\n"
    for file in all_files:
        request_text += file.get_list_text() + "\n"
    request_text += "=" * 8 + "\n"

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

def generation_request(user_id, model_type, prompt, response_format, tools=None):
    user_obj = ARUser.objects.get(id=user_id)
    api_key = user_obj.gemini_key_encrypted
    client = genai.Client(api_key=api_key)

    if tools is None:
        tools = []

    ResponseFormat = response_format
    if tools:
        config = types.GenerateContentConfig(
            tools=tools,
            response_mime_type="application/json",
            response_json_schema=ResponseFormat.model_json_schema(),
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=False)
        )
    else:
        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_json_schema=ResponseFormat.model_json_schema(),
        )

    response = client.models.generate_content(
        model=model_type,
        contents=prompt,
        config=config
    )

    if not response.text:
        print("!!! 응답 생성 실패 !!!")
        try:
            print(f"Finish Reason: {response.candidates[0].finish_reason}")
            print(f"Safety Ratings: {response.candidates[0].safety_ratings}")
        except:
            print(f"Response Dump: {response}")
        
        raise ValueError("Gemini API returned an empty response. (Likely blocked by safety filters)")

    generation_result = ResponseFormat.model_validate_json(response.text)
    return generation_result

def request_folder_generation(session_id, user_id):
    current_session =  GenerationSession.objects.get(id=session_id)
    
    return generation_request(
        user_id, 
        "gemini-3-flash-preview",
        get_folder_generation_prompt(session_id),
        get_folder_to_create_list_model(current_session.project_under.name)
    )

def request_code_generation(session_id, user_id):
    current_session =  GenerationSession.objects.get(id=session_id)
    project = current_session.project_under
    related_files_ids = [file.id for file in ProjectFile.objects.filter(project_under=project)]

    folders = Folder.objects.filter(project_under=project)
    related_folders_ids = [folder.id for folder in folders]

    def file_search_function_call(file_id_list: List[int]) -> List[str]:
        """
        내용이 제공된 파일들 외에 추가로 내용을 알아야 할 파일이 있다면, 해당 파일의 ID를 리스트로 받아 해당 파일들의 내용을 조회하여 반환합니다.
        
        Args:
            file_id_list: 내용이 명시되지 않은 파일 중 내용을 확인해야만 하는 파일의 ID 값들을 담은 리스트입니다. 각 파일의 ID는 FileList 란에 [ID: {id}]와 같이 명시되어 있습니다. 반드시 FileList 란에 명시된 ID 중에서만 선택하세요.

        Returns:
            요청한 파일들의 내용들을 담은 문자열 리스트
        """

        results = []
        files = ProjectFile.objects.filter(id__in=file_id_list)
        for file in files:
            results.append(file.get_prompt_text())
        
        return results

    return generation_request(
        user_id, 
        "gemini-3-pro-preview",
        get_generation_prompt(session_id),
        get_response_format_model(related_files_ids, related_folders_ids),
        [file_search_function_call]
    )