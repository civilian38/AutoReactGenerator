from django.contrib import admin
from .models import APIDoc

@admin.register(APIDoc)
class APIDocAdmin(admin.ModelAdmin):
    fields = ('id', 'url', 'http_method', 'request_format', 'request_headers', 'query_params', 'response_format', 'description', 'created_at', 'created_by', 'project_under')
    readonly_fields = ('id', 'created_at',)