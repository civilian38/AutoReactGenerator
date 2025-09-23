from rest_framework import serializers

from project.models import Project
from .models import FrontPage

class FrontPageSerializer(serializers.ModelSerializer):
    project_under = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = FrontPage
        fields = '__all__'
        read_only_fields = ('is_implemented', 'project_under')

class FrontPageListSerializer(serializers.ModelSerializer):
    class Meta:
        model = FrontPage
        fields = ['id', 'url', 'is_implemented']