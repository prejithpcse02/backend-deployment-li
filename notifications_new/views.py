from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Notification
from .serializers import NotificationSerializer
from .services import NotificationService
from django.contrib.auth import get_user_model

User = get_user_model()

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notification_list(request):
    """
    List all notifications for the current user
    """
    unread_only = request.query_params.get('unread', False)
    queryset = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    
    if unread_only:
        queryset = queryset.filter(is_read=False)
    
    serializer = NotificationSerializer(queryset, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_notification_read(request, notification_id):
    """
    Mark a single notification as read
    """
    try:
        notification = Notification.objects.get(id=notification_id, recipient=request.user)
        notification.mark_as_read()
        return Response({'status': 'notification marked as read'})
    except Notification.DoesNotExist:
        return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_all_notifications_read(request):
    """
    Mark all notifications as read
    """
    NotificationService.mark_notifications_as_read(request.user)
    return Response({'status': 'all notifications marked as read'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_unread_count(request):
    """
    Get count of unread notifications
    """
    count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    return Response({'unread_count': count})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_device(request):
    """
    Register a device token for push notifications
    """
    token = request.data.get('token')
    if not token:
        return Response({'error': 'Token is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Create or update device token
    device_token, created = request.user.device_tokens.get_or_create(
        token=token,
        defaults={'is_active': True}
    )
    
    if not created:
        device_token.is_active = True
        device_token.save()
    
    return Response({'status': 'device registered successfully'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unregister_device(request):
    """
    Unregister a device token
    """
    token = request.data.get('token')
    if not token:
        return Response({'error': 'Token is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Mark device token as inactive
    request.user.device_tokens.filter(token=token).update(is_active=False)
    return Response({'status': 'device unregistered successfully'})
