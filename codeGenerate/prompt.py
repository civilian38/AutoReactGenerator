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
code_generate_final_message="위 정보를 종합하여 즉시 배포 가능한 수준의 코드를 작성하세요. **코드를 모두 작성한 후에는, 반드시 [Protocol: Handover Context] 섹션에서 정의한 양식에 맞춰 인계 사항을 출력해야 합니다.**"