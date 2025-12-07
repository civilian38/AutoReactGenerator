from rest_framework import serializers

from AutoReactGenerator.permissions import IsOwnerOrReadOnly
from .models import Project

class ProjectLCSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)

    def validate_base_url(self, value):
        return value.rstrip('/')
    
    class Meta:
        model = Project
        fields = ['id', 'name', 'base_url', 'description', 'created_by', 'created_at']