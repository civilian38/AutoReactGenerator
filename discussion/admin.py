from django.contrib import admin

from discussion.models import *

admin.site.register(Discussion)
admin.site.register(DiscussionChat)