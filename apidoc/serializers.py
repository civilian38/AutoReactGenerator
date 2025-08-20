from rest_framework import serializers

from .models import APIDoc

class APIDocSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    project_under = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = APIDoc
        fields = '__all__'

class APIDocCreateSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    project_under = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = APIDoc
        fields = '__all__'


class APIDocListSerializer(serializers.ModelSerializer):
    class Meta:
        model = APIDoc
        fields = ['id', 'url', 'http_method']