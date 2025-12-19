from django.contrib import admin
from .models import *

admin.site.register(DraftFile)

class DraftFileInline(admin.TabularInline):
    model = DraftFile

@admin.register(ProjectFile)
class ProjectFileAdmin(admin.ModelAdmin):
    fields = ('id', 'name', 'content', 'created_at', 'updated_at', 'project_under', 'folder')
    readonly_fields = ('id', 'created_at', 'updated_at')
    inlines = [DraftFileInline]

@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    fields = ('id', 'parent_folder', 'name', 'project_under')
    readonly_fields = ('id',)
