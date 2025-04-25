from django.contrib.contenttypes.models import ContentType
from .models import Notification
from .views import send_push_notification

def create_notification(recipient, sender, notification_type, text, content_object=None):
    """
    Create a notification and send a push notification
    
    Args:
        recipient: User who will receive the notification
        sender: User who triggered the notification
        notification_type: Type of notification (like, offer, message, etc.)
        text: Text content of the notification
        content_object: Related object (optional)
    
    Returns:
        The created notification object
    """
    # Don't create notification if sender is the recipient
    if sender.id == recipient.id:
        return None
        
    # Create notification
    notification = Notification.objects.create(
        recipient=recipient,
        sender=sender,
        notification_type=notification_type,
        text=text
    )
    
    # Add related object if provided
    if content_object:
        content_type = ContentType.objects.get_for_model(content_object)
        notification.content_type = content_type
        notification.object_id = str(content_object.pk)
        notification.save()
    
    # Send push notification
    send_push_notification(notification)
    
    return notification 