from django.shortcuts import render, get_object_or_404
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import Notification, DeviceToken
from .serializers import NotificationSerializer
from .services import NotificationService

User = get_user_model()

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def notification_list(request):
    """
    List all notifications for the authenticated user
    """
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    serializer = NotificationSerializer(notifications, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_notification_read(request, notification_id):
    """
    Mark a single notification as read
    """
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.mark_as_read()
    return Response({'status': 'success'}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_all_notifications_read(request):
    """
    Mark all notifications as read
    """
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return Response({'status': 'success'}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_unread_count(request):
    """
    Get count of unread notifications
    """
    count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    return Response({'count': count})

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def register_device(request):
    """
    Register a device token for push notifications
    """
    token = request.data.get('device_token')
    device_type = request.data.get('device_type', 'android')
    
    if not token:
        return Response({'error': 'Device token is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    device_token, created = DeviceToken.objects.update_or_create(
        token=token,
        defaults={
            'user': request.user,
            'device_type': device_type,
            'is_active': True
        }
    )
    
    return Response({
        'status': 'success',
        'created': created
    }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def unregister_device(request):
    """
    Unregister a device token
    """
    token = request.data.get('device_token')
    
    if not token:
        return Response({'error': 'Device token is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        device_token = DeviceToken.objects.get(token=token, user=request.user)
        device_token.is_active = False
        device_token.save()
        return Response({'status': 'success'}, status=status.HTTP_200_OK)
    except DeviceToken.DoesNotExist:
        return Response({'error': 'Device token not found'}, status=status.HTTP_404_NOT_FOUND)
