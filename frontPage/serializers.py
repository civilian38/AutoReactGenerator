from django.core.validators import URLValidator
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from project.models import Project
from .models import FrontPage

class FrontPageSerializer(serializers.ModelSerializer):
    project_under = serializers.PrimaryKeyRelatedField(read_only=True)
    url = serializers.CharField()

    class Meta:
        model = FrontPage
        fields = '__all__'
        read_only_fields = ('is_implemented', 'project_under')

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

        if project and project.base_web_url:
            if incoming_url.startswith(project.base_web_url):
                attrs['url'] = incoming_url.rstrip('/')
                return attrs

            base = project.base_web_url.rstrip('/')
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

class FrontPageListSerializer(serializers.ModelSerializer):
    class Meta:
        model = FrontPage
        fields = ['id', 'url', 'is_implemented']