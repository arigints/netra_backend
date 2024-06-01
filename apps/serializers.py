from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from .models import UserProfile, PcapFile

class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data.get('password'))
        return super(UserCreateSerializer, self).create(validated_data)

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['level', 'completion']

class UserListSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'profile']

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
            'username': {'required': False}
        }

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        password = validated_data.get('password')
        if password:
            instance.set_password(password)
        instance.save()
        return instance

class UserInformationSerializer(serializers.ModelSerializer):
    level = serializers.IntegerField(source='profile.level')
    completion = serializers.FloatField(source='profile.completion')

    class Meta:
        model = User
        fields = ['username', 'level', 'completion']

class PcapFileSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)  # Use username instead of user ID

    class Meta:
        model = PcapFile
        fields = ['id', 'user', 'filename', 'file_size', 'created_at']  # Exclude file_data field
        read_only_fields = ['id', 'user', 'filename', 'file_size', 'created_at']