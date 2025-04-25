from rest_framework import serializers
from .models import Notification
from django.contrib.auth import get_user_model

User = get_user_model()

class UserMinimalSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'nickname', 'avatar', 'email']

    def get_avatar(self, obj):
        # If the user has a profile picture, return its URL
        if hasattr(obj, 'profile_picture') and obj.profile_picture:
            return obj.profile_picture.url
        return None

class NotificationSerializer(serializers.ModelSerializer):
    sender = UserMinimalSerializer(read_only=True, allow_null=True)
    message = serializers.CharField(source='text')
    
    class Meta:
        model = Notification
        fields = [
            'id', 
            'recipient',
            'sender',
            'notification_type',
            'message',
            'is_read',
            'created_at',
            'content_type',
            'object_id'
        ]
        read_only_fields = ['recipient', 'sender', 'notification_type', 'message', 'created_at', 'content_type', 'object_id'] 