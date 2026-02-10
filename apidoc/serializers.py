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
        read_only_fields = ('method_order',)

class APIDocCreateSerializer(serializers.ModelSerializer):
    url = serializers.CharField()
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    project_under = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = APIDoc
        fields = '__all__'
        read_only_fields = ('method_order',)

    def validate(self, attrs):
        incoming_url = attrs.get('url', '')

        view = self.context.get('view')
        project_id = view.kwargs.get('project_id')

        project = None
        if project_id:
            try:
                project = Project.objects.get(pk=project_id)
            except Project.DoesNotExist:
                raise ValidationError('Project does not exist')

        if project and project.base_api_url:
            if incoming_url.startswith(project.base_api_url):
                attrs['url'] = incoming_url.rstrip('/') + '/'
                return attrs

            base = project.base_api_url.rstrip('/')
            path = incoming_url.strip('/')
            full_url = f"{base}/{path}/"

            # 유효성 재검사
            validator = URLValidator()
            try:
                validator(full_url)
            except ValidationError:
                raise serializers.ValidationError({"url": "INVALID URL TYPE"})
            attrs['url'] = full_url
        return attrs

class APIDocListSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = APIDoc
        fields = ['id', 'url', 'http_method']

    def get_url(self, obj):
        project = obj.project_under
        if project and project.base_api_url:
            return obj.url.removeprefix(project.base_api_url.rstrip('/'))
        return "Unknown Error"
