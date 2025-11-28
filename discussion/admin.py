from django.contrib import admin

from discussion.models import *

admin.site.register(DiscussionChat)

class DiscussionChatInline(admin.TabularInline):
    model = DiscussionChat
    extra = 1

@admin.register(Discussion)
class DiscussionAdmin(admin.ModelAdmin):
    fields = ('id', 'title', 'summary', 'project_under', 'created_at', 'updated_at')
    readonly_fields = ('id', 'created_at', 'updated_at')
    inlines = [DiscussionChatInline]
