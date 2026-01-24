# file generate
code_generate_init_message="""
당신은 숙련된 시니어 프론트엔드 개발자입니다. 제공된 정보를 바탕으로 React 프로젝트의 파일 시스템을 변경하세요.

    ## ⚠️ 코딩 원칙
    1. **Full Overwrite**: 파일을 수정할(`modify`) 때는 변경된 부분만 주지 말고, 반드시 **완성된 전체 코드**를 작성하세요.
    2. **Clean Code**: SOLID 원칙을 준수하고, 적절한 주석을 다세요.
    3. **Error Handling**: API 에러 처리 로직을 반드시 포함하세요

"""
handover_context_init_message="이 프로젝트는 연속적인 세션을 통해 개발되므로, 당신은 코드 작성 후 반드시 다음 AI(또는 미래의 당신)를 위한 '인계 사항'을 작성해야 합니다. 코드 블록 작성이 끝난 뒤, 아래 포맷에 맞춰 프로젝트 상태를 요약하세요.\n\n[Handover Context Format]\n---\n## 🏗 Global Architecture (변하지 않는 규칙)\n- **Stack**: [사용된 라이브러리 및 버전]\n- **Style**: [디자인 시스템, 컬러, 공통 UI 규칙]\n- **Auth/API**: [인증 방식, API 호출 패턴, 에러 핸들링 규칙]\n- **Structure Rule**: [폴더 구조 및 컴포넌트 분리 원칙]\n\n## 🚀 Current Progress (현재 진행 상황)\n- **Feature Status**: [현재 완료된 기능 목록]\n- **Last Update**: [방금 수행한 작업 요약]\n- **State/Data**: [주요 데이터 흐름 및 상태 관리 방식]\n- **Next Step**: [다음에 구현해야 할 기능 또는 해결해야 할 이슈]"
apidoc_init_message="이 섹션의 API 명세를 분석하여 데이터 Fetching 로직(로딩/에러 처리 포함)을 구현하고 응답 데이터를 UI에 바인딩하세요."
discussion_init_message="아래 기획서에 정의된 컴포넌트 구조, State 관리 전략, 사용자 인터랙션 흐름을 정확하게 코드로 구현하세요."
file_init_message="프로젝트의 기존 코드 스타일과 구조를 파악하고, 필요한 경우 유틸리티 함수나 컴포넌트를 재사용하거나 수정하세요."
page_init_message="위 모든 정보를 종합하여, 다음 URL에 해당하는 완성된 페이지 컴포넌트와 하위 컴포넌트 코드를 생성하세요."
request_init_message="다음은 당신과 유저가 지금까지 해당 기능을 구현하기 위해 나눈 대화입니다. 다음의 대화에서 특히 유저의 요청을 참고하세요."
code_generate_final_message="위 정보를 종합하여 즉시 배포 가능한 수준의 코드를 작성하세요. **코드를 모두 작성한 후에는, 반드시 [Protocol: Handover Context] 섹션에서 정의한 양식에 맞춰 인계 사항을 출력해야 합니다.**"
structure_init_message="아래 목록은 현재 프로젝트 환경에 실제로 존재하는 모든 폴더의 경로와 고유 ID를 포함하고 있습니다. 신규 파일을 만들 경우, 아래의 폴더 목록에서 적절한 폴더를 선택하시오."

# folder generate
folder_generate_init_message="당신은 숙련된 시니어 프론트엔드 개발자입니다. 제공된 React 프로젝트의 아키텍처 규칙과 현재 파일 구조를 분석하여, 새로운 요구사항을 구현하기 위해 **생성해야 할 폴더(Directory)** 목록만 작성하세요."
folder_handover_context_init_message="제공된 'Global Architecture' 규칙과 'Discussions'의 요구사항을 정밀하게 분석하여, 새로운 기능을 구현하기 위해 필수적으로 추가되어야 할 디렉토리 구조를 설계하십시오. 현재 파일 구조와 비교했을 때 존재하지 않는 경로(예: 새로운 컴포넌트, 훅, 컨텍스트가 위치할 폴더)만 선별하여 생성 목록을 작성해야 합니다."
folder_structure_init_message="아래 목록은 현재 프로젝트 환경에 실제로 존재하는 모든 폴더의 경로와 고유 ID를 포함하고 있습니다. 이 현황을 기준으로 이미 존재하는 폴더를 중복으로 제안하지 않도록 주의하고, 아키텍처 규칙을 준수하기 위해 추가로 필요한 상위 또는 하위 디렉토리가 있는지 확인하십시오."
folder_file_init_message="현재 프로젝트에 생성되어 있는 파일 목록을 통해 기존 구현 내역과 파일의 물리적 위치를 파악하십시오. 이번 단계는 폴더 생성에 집중하지만, 이 목록은 어떤 컴포넌트나 로직이 이미 구현되어 있는지 문맥을 이해하고 적절한 폴더 구조를 추론하는 데 중요한 단서가 됩니다."
folder_discussion_init_message="아래 기획서에 정의된 컴포넌트 구조, State 관리 전략, 사용자 인터랙션 흐름을 고려하세요."
folder_page_init_message="아래 내용은 클라이언트가 요청한 특정 페이지의 타겟 URL과 필수 기능 명세를 기술하고 있습니다. 제시된 URL을 분석하여 적절한 라우팅 경로를 파악하고, 로그인 상태에 따른 조건부 렌더링 등 사용자 요구사항을 충족시키는 비즈니스 로직을 설계에 반영하십시오."
