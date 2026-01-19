from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import ARUser

@admin.register(ARUser)
class ARUserAdmin(UserAdmin):
    list_display = ('id', 'username', 'nickname', 'email', 'is_active')
    
    list_display_links = ('id', 'username')

    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('nickname', 'bio', 'gemini_key_encrypted')}),
    )