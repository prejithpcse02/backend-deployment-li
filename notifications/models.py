from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from model_utils import FieldTracker

User = get_user_model()

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('like', 'Like'),
        ('offer', 'Offer'),
        ('message', 'Message'),
        ('review', 'Review'),
        ('price_update', 'Price Update'),
        ('item_sold', 'Item Sold'),
        ('new_listing', 'New Listing'),
    )
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications', null=True, blank=True)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    text = models.CharField(max_length=255)
    
    # Generic relation to the related object
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.CharField(max_length=50, null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_push_sent = models.BooleanField(default=False)
    
    tracker = FieldTracker()
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.sender.username if self.sender else 'System'} {self.get_notification_type_display()} notification to {self.recipient.username}"

    def mark_as_read(self):
        self.is_read = True
        self.save()

class DeviceToken(models.Model):
    """Store device tokens for push notifications"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='device_tokens')
    token = models.CharField(max_length=255, unique=True)
    device_type = models.CharField(max_length=10, choices=[('ios', 'iOS'), ('android', 'Android')], default='android')
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    tracker = FieldTracker()
    
    class Meta:
        unique_together = ('user', 'token')
        
    def __str__(self):
        return f"{self.user.username}'s {self.device_type} device"
