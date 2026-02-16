from django.contrib import admin
from django.utils.html import format_html
# URLParameter 모델을 임포트 추가해야 합니다.
from .models import APIDoc, APIRequestBody, APIResponseBody, URLParameter

# 1. APIDoc 내부에서 Request/Response Body를 바로 편집할 수 있도록 Inline 정의
class APIRequestBodyInline(admin.StackedInline):
    model = APIRequestBody
    extra = 0
    classes = ['collapse']

class APIResponseBodyInline(admin.StackedInline):
    model = APIResponseBody
    extra = 0
    classes = ['collapse']

# [NEW] URLParameter를 독립적으로 관리하기 위한 Admin 설정
@admin.register(URLParameter)
class URLParameterAdmin(admin.ModelAdmin):
    list_display = ('parameter', 'description', 'project_under')
    list_filter = ('project_under',)
    search_fields = ('parameter', 'description')
    ordering = ('project_under', 'parameter')

# 2. APIDoc Admin 설정
@admin.register(APIDoc)
class APIDocAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'project_under', 
        'get_colored_method', 
        'url', 
        'get_url_params_display', # [NEW] 리스트에서 파라미터 확인용 함수 추가
        'created_by', 
        'created_at'
    )
    
    list_display_links = ('id', 'url')
    
    list_filter = ('project_under', 'http_method', 'created_by')
    
    search_fields = ('url', 'description', 'project_under__title')
    
    inlines = [APIRequestBodyInline, APIResponseBodyInline]
    
    # [NEW] ManyToMany 필드인 url_parameters를 좌우 선택 박스(UI)로 보여줍니다.
    # 데이터가 많을 때 선택하기 가장 편리한 방식입니다.
    filter_horizontal = ('url_parameters',)

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

    # [NEW] 연결된 URL Parameter들을 리스트 화면에서 간단히 보여주는 메서드
    def get_url_params_display(self, obj):
        params = obj.url_parameters.all()
        if params.exists():
            return ", ".join([p.parameter for p in params])
        return "-"
    get_url_params_display.short_description = "URL Params"


# 3. APIRequestBody Admin 설정
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
        return f"{obj.http_status} ({obj.get_http_status_display()})"
    get_status_display.short_description = "HTTP Status"

    def short_description(self, obj):
        return (obj.description[:50] + '...') if obj.description and len(obj.description) > 50 else obj.description
    short_description.short_description = "설명 요약"