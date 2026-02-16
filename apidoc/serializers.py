from django.core.validators import URLValidator
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from project.models import Project
from .models import APIDoc, APIRequestBody, APIResponseBody, URLParameter

class APIRequestBodySerializer(serializers.ModelSerializer):
    apidoc = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = APIRequestBody
        fields = '__all__'

class APIRequestListSerializer(serializers.ModelSerializer):
    description = serializers.SerializerMethodField()
    class Meta:
        model = APIRequestBody
        fields = ('id', 'description')

    def get_description(self, obj):
        description = obj.description
        return description[:30]

class APIResponseBodySerializer(serializers.ModelSerializer):
    apidoc = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = APIResponseBody
        fields = '__all__'

class APIResponseListSerializer(serializers.ModelSerializer):
    description = serializers.SerializerMethodField()
    class Meta:
        model = APIResponseBody
        fields = ('id', 'http_status', 'description')

    def get_description(self, obj):
        description = obj.description
        return description[:30]
    
class URLParameterListSerializer(serializers.ModelSerializer):
    class Meta:
        model = URLParameter
        fields = ('id', 'parameter', 'description')

class APIDocSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    project_under = serializers.PrimaryKeyRelatedField(read_only=True)
    request_bodies = APIRequestListSerializer(many=True, read_only=True)
    response_bodies = APIResponseListSerializer(many=True, read_only=True)
    url_parameters = URLParameterListSerializer(many=True, read_only=True)

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

class URLParameterCreateSerializer(serializers.ModelSerializer):
    project_under = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = URLParameter
        fields = ('id', 'project_under', 'parameter', 'description')

class URLParameterRetrieveUpdateSerializer(serializers.ModelSerializer):
    apidocs = APIDocListSerializer(many=True, read_only=True)

    class Meta:
        model = URLParameter
        fields = ('parameter', 'description', 'apidocs')

class ParameterRelationUpdateSerializer(serializers.Serializer):
    to_add = serializers.ListField(child=serializers.IntegerField(), required=False, default=[])
    to_pop = serializers.ListField(child=serializers.IntegerField(), required=False, default=[])

    class Meta:
        fields = ('to_add', 'to_pop')