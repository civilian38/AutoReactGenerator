from rest_framework import serializers
from .models import ARUser

class ARUserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = ARUser
        fields = ('username', 'password', 'nickname', 'email', 'bio', 'gemini_key_encrypted')
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': False}, 
        }

    def create(self, validated_data):
        user = ARUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            gemini_key_encrypted=validated_data['gemini_key_encrypted'],
            nickname=validated_data.get('nickname', ''),
            bio=validated_data.get('bio', '')
        )
        return user

class GeminiKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = ARUser
        fields = ('gemini_key_encrypted',)

class ARUserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ARUser
        fields = ('username', 'email', 'nickname', 'bio')