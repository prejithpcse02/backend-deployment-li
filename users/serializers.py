from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user details"""
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'nickname', 'avatar', 'is_verified', 'created_at']
        read_only_fields = ['id', 'is_verified', 'created_at']


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new users"""
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['email', 'username', 'nickname', 'password', 'password_confirm', 'avatar']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        # Remove password_confirm from the data
        validated_data.pop('password_confirm')
        
        # Create the user
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['email'],
            nickname=validated_data['nickname'],
            password=validated_data['password']
        )
        
        # Add profile picture if it exists
        if 'avatar' in validated_data:
            user.avatar = validated_data['avatar']
            user.save()
            
        return user 