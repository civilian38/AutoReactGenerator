from rest_framework import serializers

from .models import FrontFile

class FrontFileSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    project_under = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = FrontFile
        fields = '__all__'

class FrontFileCreateSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    project_under = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = FrontFile
        fields = '__all__'


class FrontFileListSerializer(serializers.ModelSerializer):
    class Meta:
        model = FrontFile
        fields = ['id', 'address', 'updated_at']