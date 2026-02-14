from rest_framework import serializers

from .models import Project
from authentication.serializers import ARUserInfoSerializer

class ProjectListSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'name', 'base_web_url', 'description', 'created_by', 'created_at']

class ProjectCreateSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)

    def validate_base_web_url(self, value):
        return value.rstrip('/')

    def validate_base_api_url(self, value):
        return value.rstrip('/') + '/'
    
    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ('handover_context', 'handover_draft', 'to_do_request')

class ProjectRetrieveUpdateDestroySerializer(serializers.ModelSerializer):
    created_by = ARUserInfoSerializer(read_only=True)
    handover_text = serializers.CharField(source='get_prompt_text', read_only=True)

    class Meta:
        model = Project
        fields = ('id', 'name', 'base_api_url', 'base_web_url', 'description', 'instruction', 'created_by', 'created_at', 'handover_text', 'to_do_request')
        read_only_fields = ('id', 'created_by', 'created_at', 'handover_text', 'to_do_request')

"""
Only For Test
"""

class TestProjectSerializer(serializers.ModelSerializer):
    created_by = ARUserInfoSerializer(read_only=True)

    class Meta:
        model = Project
        fields = '__all__'