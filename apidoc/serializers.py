from rest_framework import serializers

from .models import APIDoc

class APIDocSerializer(serializers.ModelSerializer):
    class Meta:
        model = APIDoc
        fields = '__all__'

class APIDocCreateSerializer(serializers.ModelSerializer):
    project_under = serializers.HiddenField(default=None) 
    class Meta:
        model = APIDoc
        fields = '__all__'


class APIDocListSerializer(serializers.ModelSerializer):
    class Meta:
        model = APIDoc
        fields = ['id', 'url', 'http_method']