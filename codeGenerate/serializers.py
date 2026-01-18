from rest_framework import serializers

from .models import *

class GenerationSessionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = GenerationSession
        fields = ['id', 'title', 'status', 'is_occupied', 'created_at']
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
            'id', 'project_under', 'title', 'is_occupied',
            'related_apidocs', 'related_discussions', 
            'related_folders', 'related_files', 'related_pages'
        ]
        read_only_fields = ('is_occupied',)

    def validate(self, attrs):
        view = self.context.get('view')
        project_id = view.kwargs.get('project_id')
        try:
            project_under = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            raise serializers.ValidationError("존재하지 않는 프로젝트입니다.")
        
        if GenerationSession.objects.filter(project_under=project_under, status='ACTIVE').exists():
            raise serializers.ValidationError(
                "해당 프로젝트에 이미 진행 중인(ACTIVE) 세션이 존재합니다. 기존 세션을 완료하거나 폐기해주세요."
            )
        
        if project_under.to_do_request:
            raise serializers.ValidationError(
                "요청 사항이 수락되지 않았습니다. 요청 사항을 수행한 뒤, 수락 버튼을 누르고 다시 시도하십시오."
            )
        
        attrs['project_under'] = project_under
        return attrs

    def create(self, validated_data):
        validated_data['status'] = 'ACTIVE'
        return super().create(validated_data)

class SessionChatUserInputSerializer(serializers.ModelSerializer):
    session_under = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = SessionChat
        fields = '__all__'
        read_only_fields = ('is_by_user', 'created_at')

class SessionChatListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionChat
        fields = ('content', 'created_at', 'is_by_user')
        read_only_fields = fields