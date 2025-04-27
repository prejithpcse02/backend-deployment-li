from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from listings.models import Listing
from rest_framework.exceptions import PermissionDenied, NotFound
import logging

logger = logging.getLogger(__name__)

class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(
            participants=self.request.user,
            is_active=True
        ).order_by('-updated_at')

    def create(self, request, *args, **kwargs):
        listing_id = request.data.get('listing')
        try:
            listing = Listing.objects.get(product_id=listing_id)
        except Listing.DoesNotExist:
            return Response({"error": "Listing not found"}, status=status.HTTP_404_NOT_FOUND)

        # Check if conversation already exists
        conversation = Conversation.objects.filter(
            listing=listing,
            participants=request.user,
            is_active=True
        ).first()

        if conversation:
            return Response(ConversationSerializer(conversation).data)

        conversation = Conversation.objects.create(listing=listing)
        conversation.participants.add(request.user, listing.seller)
        return Response(ConversationSerializer(conversation).data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        conversation = self.get_object()
        if request.user not in conversation.participants.all():
            raise PermissionDenied("You are not a participant in this conversation")
        
        conversation.is_active = False
        conversation.save()
        return Response({"status": "conversation archived"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        conversation = self.get_object()
        if request.user not in conversation.participants.all():
            raise PermissionDenied("You are not a participant in this conversation")
            
        messages = conversation.messages.filter(is_deleted=False).order_by('created_at')
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        conversation = self.get_object()
        if request.user not in conversation.participants.all():
            raise PermissionDenied("You are not a participant in this conversation")
            
        conversation.is_active = False
        conversation.save()
        return Response({"status": "conversation archived"}, status=status.HTTP_200_OK)

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Message.objects.filter(
            Q(conversation__participants=self.request.user) &
            Q(is_deleted=False)
        ).order_by('created_at')

    def create(self, request, *args, **kwargs):
        logger.info(f"Received message creation request with data: {request.data}")
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            logger.error(f"Error creating message: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        conversation = serializer.validated_data['conversation']
        if self.request.user not in conversation.participants.all():
            raise PermissionDenied("You are not a participant in this conversation")
        serializer.save(sender=self.request.user)

    def destroy(self, request, *args, **kwargs):
        message = self.get_object()
        if message.sender != request.user:
            raise PermissionDenied("You can only delete your own messages")
            
        message.is_deleted = True
        message.deleted_at = timezone.now()
        message.save()
        return Response({"status": "message deleted"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        message = self.get_object()
        if request.user not in message.conversation.participants.all():
            raise PermissionDenied("You are not a participant in this conversation")
            
        message.is_read = True
        message.save()
        return Response({"status": "message marked as read"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def delete(self, request, pk=None):
        message = self.get_object()
        if message.sender != request.user:
            raise PermissionDenied("You can only delete your own messages")
            
        message.is_deleted = True
        message.deleted_at = timezone.now()
        message.save()
        return Response({"status": "message deleted"}, status=status.HTTP_200_OK) 