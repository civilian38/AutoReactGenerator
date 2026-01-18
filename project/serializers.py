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
        read_only_fields = ('handover_context', 'to_do_request')

class ProjectRetrieveSerializer(serializers.ModelSerializer):
    created_by = ARUserInfoSerializer(read_only=True)

    class Meta:
        model = Project
        fields = '__all__'