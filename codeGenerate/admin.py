from django.contrib import admin

from .models import GenerationSession, SessionChat
from project.models import Project
from apidoc.models import APIDoc
from discussion.models import Discussion
from frontFile.models import Folder, ProjectFile
from frontPage.models import FrontPage

admin.site.register(SessionChat)

@admin.register(GenerationSession)
class GenerationSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'project_under', 'status', 'created_at']
    
    filter_horizontal = [
        'related_apidocs', 
        'related_discussions', 
        'related_folders', 
        'related_files', 
        'related_pages'
    ]