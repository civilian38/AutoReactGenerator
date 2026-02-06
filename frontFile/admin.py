from django.contrib import admin
from .models import *

admin.site.register(ProjectFile)

@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    fields = ('id', 'parent_folder', 'name', 'project_under', 'description')
    readonly_fields = ('id',)