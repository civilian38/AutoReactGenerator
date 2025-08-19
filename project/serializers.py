from rest_framework import serializers

from AutoReactGenerator.permissions import IsOwnerOrReadOnly
from .models import Project

class ProjectLCSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'created_by', 'created_at']