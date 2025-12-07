from django.core.validators import URLValidator
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from project.models import Project
from .models import APIDoc

class APIDocSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    project_under = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = APIDoc
        fields = '__all__'

class APIDocCreateSerializer(serializers.ModelSerializer):
    url = serializers.CharField()
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    project_under = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = APIDoc
        fields = '__all__'

    def validate(self, attrs):
        incoming_url = attrs.get('url', '')

        if incoming_url.startswith(('http://', 'https://')):
            return attrs

        view = self.context.get('view')
        project_id = view.kwargs.get('project_id')

        project = None
        if project_id:
            try:
                project = Project.objects.get(pk=project_id)
            except Project.DoesNotExist:
                raise ValidationError('Project does not exist')

        if project and project.base_url:
            base = project.base_url.rstrip('/')
            path = incoming_url.strip('/')
            full_url = f"{base}/{path}"

            # 유효성 재검사
            validator = URLValidator()
            try:
                validator(full_url)
            except ValidationError:
                raise serializers.ValidationError({"url": "INVALID URL TYPE"})
            attrs['url'] = full_url
        return attrs

class APIDocListSerializer(serializers.ModelSerializer):
    class Meta:
        model = APIDoc
        fields = ['id', 'url', 'http_method']