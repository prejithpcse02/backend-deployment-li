from rest_framework import serializers
from .models import Conversation, Message
from users.serializers import UserSerializer
from listings.serializers import ListingSerializer

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    sender_id = serializers.IntegerField(write_only=True)
    conversation = serializers.PrimaryKeyRelatedField(queryset=Conversation.objects.all())
    
    class Meta:
        model = Message
        fields = ['id', 'conversation', 'sender', 'sender_id', 'content', 'message_type', 'file_url', 
                 'is_read', 'created_at', 'updated_at', 'is_deleted']
        read_only_fields = ['sender', 'created_at', 'updated_at']

    def validate(self, data):
        request = self.context.get('request')
        if request and request.user:
            conversation = data.get('conversation')
            if conversation and request.user not in conversation.participants.all():
                raise serializers.ValidationError("You are not a participant in this conversation")
        return data

class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    listing = ListingSerializer(read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    other_participant = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['id', 'listing', 'participants', 'last_message', 'unread_count', 
                 'created_at', 'updated_at', 'is_active', 'other_participant']
        read_only_fields = ['created_at', 'updated_at']

    def get_last_message(self, obj):
        last_message = obj.messages.filter(is_deleted=False).last()
        if last_message:
            return MessageSerializer(last_message).data
        return None

    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.messages.filter(is_read=False, is_deleted=False).exclude(sender=request.user).count()
        return 0

    def get_other_participant(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            other_participant = obj.participants.exclude(id=request.user.id).first()
            if other_participant:
                return UserSerializer(other_participant).data
        return None 