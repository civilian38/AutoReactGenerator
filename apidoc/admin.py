from django.contrib import admin
from django.utils.html import format_html
from .models import APIDoc, APIRequestBody, APIResponseBody

# 1. APIDoc 내부에서 Request/Response Body를 바로 편집할 수 있도록 Inline 정의
class APIRequestBodyInline(admin.StackedInline):
    model = APIRequestBody
    extra = 0  # 기본으로 보여주는 빈 칸 수 (0으로 설정하여 깔끔하게 유지)
    classes = ['collapse'] # 내용이 길어질 수 있으므로 접을 수 있게 설정

class APIResponseBodyInline(admin.StackedInline):
    model = APIResponseBody
    extra = 0
    classes = ['collapse']

# 2. APIDoc Admin 설정
@admin.register(APIDoc)
class APIDocAdmin(admin.ModelAdmin):
    # ID를 맨 앞에 배치하여 식별 용이하게 설정
    list_display = (
        'id', 
        'project_under', 
        'get_colored_method', # 메서드에 색상을 입힌 함수
        'url', 
        'created_by', 
        'created_at'
    )
    
    # ID나 URL을 클릭하면 수정 페이지로 이동
    list_display_links = ('id', 'url')
    
    # 우측 필터 옵션
    list_filter = ('project_under', 'http_method', 'created_by')
    
    # 검색 기능 (URL, 설명, 프로젝트 이름 등)
    search_fields = ('url', 'description', 'project_under__title') # project에 title 필드가 있다고 가정
    
    # 상세 페이지에서 연관된 Body 모델들을 같이 보여줌
    inlines = [APIRequestBodyInline, APIResponseBodyInline]
    
    # 데이터가 많을 경우 드롭다운 대신 돋보기 팝업 사용 (선택 사항)
    # raw_id_fields = ('project_under', 'created_by')

    # HTTP Method에 따라 색상을 다르게 표시하는 메서드
    def get_colored_method(self, obj):
        colors = {
            'GET': 'blue',
            'POST': 'green',
            'PUT': 'orange',
            'PATCH': 'orange',
            'DELETE': 'red',
        }
        color = colors.get(obj.http_method, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.http_method
        )
    get_colored_method.short_description = 'Method'


# 3. APIRequestBody Admin 설정 (개별적으로 볼 경우를 대비)
@admin.register(APIRequestBody)
class APIRequestBodyAdmin(admin.ModelAdmin):
    list_display = ('id', 'apidoc', 'short_description')
    list_display_links = ('id', 'apidoc')
    search_fields = ('description', 'apidoc__url')
    
    def short_description(self, obj):
        return (obj.description[:50] + '...') if obj.description and len(obj.description) > 50 else obj.description
    short_description.short_description = "설명 요약"


# 4. APIResponseBody Admin 설정
@admin.register(APIResponseBody)
class APIResponseBodyAdmin(admin.ModelAdmin):
    list_display = ('id', 'apidoc', 'get_status_display', 'short_description')
    list_display_links = ('id', 'apidoc')
    list_filter = ('http_status',)
    search_fields = ('description', 'apidoc__url')

    def get_status_display(self, obj):
        # HttpStatus Enum의 라벨을 가져오거나 상태 코드를 표시
        return f"{obj.http_status} ({obj.get_http_status_display()})"
    get_status_display.short_description = "HTTP Status"

    def short_description(self, obj):
        return (obj.description[:50] + '...') if obj.description and len(obj.description) > 50 else obj.description
    short_description.short_description = "설명 요약"