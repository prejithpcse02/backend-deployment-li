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
    product_id = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()
    
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
            'object_id',
            'product_id',
            'slug'
        ]
        read_only_fields = ['recipient', 'sender', 'notification_type', 'message', 'created_at', 'content_type', 'object_id', 'product_id', 'slug']

    def get_product_id(self, obj):
        try:
            # Split the object_id to get slug and product_id
            parts = obj.object_id.split(':')
            if len(parts) == 2:
                return parts[1]  # product_id is the second part
        except Exception:
            pass
        return None

    def get_slug(self, obj):
        try:
            # Split the object_id to get slug and product_id
            parts = obj.object_id.split(':')
            if len(parts) == 2:
                return parts[0]  # slug is the first part
        except Exception:
            pass
        return None 