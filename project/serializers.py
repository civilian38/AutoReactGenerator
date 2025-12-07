from rest_framework import serializers

from .models import Project
from authentication.serializers import ARUserInfoSerializer

class ProjectLCSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)

    def validate_base_url(self, value):
        return value.rstrip('/')
    
    class Meta:
        model = Project
        fields = ['id', 'name', 'base_url', 'description', 'created_by', 'created_at']

class ProjectRetrieveSerializer(serializers.ModelSerializer):
    created_by = ARUserInfoSerializer(read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'name', 'created_by', 'base_url', 'description', 'created_at']