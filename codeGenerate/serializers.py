from rest_framework import serializers

from .models import *

class GenerationSessionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = GenerationSession
        fields = ['id', 'title', 'status', 'created_at']
        read_only_fields = fields

class GenerationSessionCreateSerializer(serializers.ModelSerializer):
    project_under = serializers.PrimaryKeyRelatedField(read_only=True)
    related_apidocs = serializers.PrimaryKeyRelatedField(many=True, queryset=APIDoc.objects.all(), required=False)
    related_discussions = serializers.PrimaryKeyRelatedField(many=True, queryset=Discussion.objects.all(), required=False)
    related_folders = serializers.PrimaryKeyRelatedField(many=True, queryset=Folder.objects.all(), required=False)
    related_files = serializers.PrimaryKeyRelatedField(many=True, queryset=ProjectFile.objects.all(), required=False)
    related_pages = serializers.PrimaryKeyRelatedField(many=True, queryset=FrontPage.objects.all(), required=False)

    class Meta:
        model = GenerationSession
        fields = [
            'project_under', 'title', 
            'related_apidocs', 'related_discussions', 
            'related_folders', 'related_files', 'related_pages'
        ]

    def validate(self, attrs):
        view = self.context.get('view')
        project_id = view.kwargs.get('project_id')
        
        if GenerationSession.objects.filter(project_under_id=project_id, status='ACTIVE').exists():
            raise serializers.ValidationError(
                "해당 프로젝트에 이미 진행 중인(ACTIVE) 세션이 존재합니다. 기존 세션을 완료하거나 폐기해주세요."
            )
        
        return attrs

    def create(self, validated_data):
        validated_data['status'] = 'ACTIVE'
        return super().create(validated_data)