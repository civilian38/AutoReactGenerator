from django.contrib import admin
from .models import Project

from frontFile.models import *
from frontPage.models import *
from apidoc.models import *
from discussion.models import Discussion

class FileInline(admin.TabularInline):
    model = Folder
    extra = 1

class PageInline(admin.TabularInline):
    model = FrontPage
    extra = 1

class DocInline(admin.TabularInline):
    model = APIDoc
    extra = 1

class DiscussionInline(admin.TabularInline):
    model = Discussion
    extra = 1

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    fields = ('id', 'name', 'description', 'base_url', 'created_by', 'created_at')
    readonly_fields = ('id', 'created_at')
    inlines = [FileInline, PageInline, DocInline, DiscussionInline]