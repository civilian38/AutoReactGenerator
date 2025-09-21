from rest_framework import serializers

from .models import *

class DiscussionSerializer(serializers.ModelSerializer):
    project_under = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Discussion
        fields = '__all__'
        read_only_fields = ('summary', )

class DiscussionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discussion
        fields = ('title', 'updated_at')

class DiscussionChatSerializer(serializers.ModelSerializer):
    discussion_under = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = DiscussionChat
        fields = '__all__'
        read_only_fields = ('is_by_user', )

class DiscussionChatLLMSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscussionChat
        fields = '__all__'