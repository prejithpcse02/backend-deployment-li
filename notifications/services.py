from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from .models import Notification, DeviceToken
import firebase_admin
from firebase_admin import credentials, messaging
import os
import json
from django.conf import settings

User = get_user_model()

class NotificationService:
    @staticmethod
    def create_notification(recipient, notification_type, text, sender=None, content_object=None):
        """
        Create a new notification
        """
        content_type = None
        object_id = None
        
        if content_object:
            content_type = ContentType.objects.get_for_model(content_object)
            object_id = str(content_object.id)
        
        notification = Notification.objects.create(
            recipient=recipient,
            sender=sender,
            notification_type=notification_type,
            text=text,
            content_type=content_type,
            object_id=object_id
        )
        
        # Send push notification
        NotificationService.send_push_notification(notification)
        
        return notification

    @staticmethod
    def create_price_update_notification(listing, old_price, new_price):
        """
        Create notification for price change in a listing
        """
        liked_users = listing.likes.all()
        
        for user in liked_users:
            NotificationService.create_notification(
                recipient=user,
                notification_type='price_update',
                text=f'The price of {listing.title} has changed from ₹{old_price} to ₹{new_price}',
                content_object=listing
            )

    @staticmethod
    def create_new_message_notification(chat_message):
        """
        Create notification for new chat message
        """
        recipient = chat_message.conversation.participants.exclude(id=chat_message.sender.id).first()
        if recipient:
            NotificationService.create_notification(
                recipient=recipient,
                notification_type='message',
                text=f'You have a new message from {chat_message.sender.username}',
                sender=chat_message.sender,
                content_object=chat_message
            )

    @staticmethod
    def create_new_listing_notification(listing):
        """
        Create notification for new listing (for followers)
        """
        followers = listing.seller.followers.all()
        for follower in followers:
            NotificationService.create_notification(
                recipient=follower,
                notification_type='new_listing',
                text=f'{listing.seller.username} has listed a new item: {listing.title}',
                sender=listing.seller,
                content_object=listing
            )

    @staticmethod
    def create_listing_liked_notification(listing, liker):
        """
        Create notification when someone likes a listing
        """
        if listing.seller != liker:
            NotificationService.create_notification(
                recipient=listing.seller,
                notification_type='like',
                text=f'{liker.username} liked your listing: {listing.title}',
                sender=liker,
                content_object=listing
            )

    @staticmethod
    def create_listing_sold_notification(listing, buyer):
        """
        Create notification when a listing is sold
        """
        NotificationService.create_notification(
            recipient=listing.seller,
            notification_type='item_sold',
            text=f'Your listing {listing.title} has been sold to {buyer.username}',
            sender=buyer,
            content_object=listing
        )

    @staticmethod
    def get_unread_notifications(user):
        """
        Get all unread notifications for a user
        """
        return Notification.objects.filter(recipient=user, is_read=False)

    @staticmethod
    def mark_notifications_as_read(user, notification_ids=None):
        """
        Mark notifications as read
        """
        if notification_ids:
            Notification.objects.filter(recipient=user, id__in=notification_ids).update(is_read=True)
        else:
            Notification.objects.filter(recipient=user, is_read=False).update(is_read=True)

    @staticmethod
    def send_push_notification(notification):
        """
        Send a push notification to a user's devices
        """
        try:
            # Initialize Firebase if not already initialized
            if not firebase_admin._apps:
                if hasattr(settings, 'FIREBASE_SERVICE_ACCOUNT') and settings.FIREBASE_SERVICE_ACCOUNT:
                    firebase_cred = credentials.Certificate(json.loads(settings.FIREBASE_SERVICE_ACCOUNT))
                else:
                    firebase_cred = credentials.Certificate(os.path.join(settings.BASE_DIR, 'firebase-service-account.json'))
                firebase_admin.initialize_app(firebase_cred)

            # Get all active device tokens for the user
            device_tokens = DeviceToken.objects.filter(
                user=notification.recipient,
                is_active=True
            ).values_list('token', flat=True)

            if not device_tokens:
                return False

            # Create the message payload
            message = messaging.MulticastMessage(
                tokens=list(device_tokens),
                notification=messaging.Notification(
                    title="Listtra Notification",
                    body=notification.text
                ),
                data={
                    'notification_id': str(notification.id),
                    'type': notification.notification_type,
                    'content_type': str(notification.content_type.id) if notification.content_type else '',
                    'object_id': notification.object_id or '',
                    'created_at': notification.created_at.isoformat()
                },
                android=messaging.AndroidConfig(
                    priority='high',
                    notification=messaging.AndroidNotification(
                        sound='default',
                        priority='high'
                    )
                ),
                apns=messaging.APNSConfig(
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(
                            sound='default',
                            content_available=True,
                            priority=10
                        )
                    )
                )
            )

            # Send the message
            response = messaging.send_multicast(message)
            
            # Mark notification as sent
            notification.is_push_sent = True
            notification.save()

            return response.success_count > 0
        except Exception as e:
            print(f"Error sending push notification: {e}")
            return False

    @staticmethod
    def create_offer_notification(offer):
        """
        Create notification for new offer
        """
        NotificationService.create_notification(
            recipient=offer.listing.user,
            notification_type='offer',
            text=f'{offer.user.username} made an offer of ₹{offer.amount} on your listing: {offer.listing.title}',
            sender=offer.user,
            content_object=offer
        )

    @staticmethod
    def create_review_notification(review):
        """
        Create notification for new review
        """
        NotificationService.create_notification(
            recipient=review.reviewed_user,
            notification_type='review',
            text=f'{review.reviewer.username} left you a {review.rating}-star review',
            sender=review.reviewer,
            content_object=review
        )

    @staticmethod
    def create_offer_accepted_notification(offer):
        """
        Create notification when an offer is accepted
        """
        NotificationService.create_notification(
            recipient=offer.user,
            notification_type='offer',
            text=f'Your offer of ₹{offer.amount} for {offer.listing.title} has been accepted!',
            sender=offer.listing.user,
            content_object=offer
        )

    @staticmethod
    def create_offer_rejected_notification(offer):
        """
        Create notification when an offer is rejected
        """
        NotificationService.create_notification(
            recipient=offer.user,
            notification_type='offer',
            text=f'Your offer of ₹{offer.amount} for {offer.listing.title} has been rejected',
            sender=offer.listing.user,
            content_object=offer
        )

    @staticmethod
    def create_listing_updated_notification(listing, changes):
        """
        Create notification when a listing is updated
        """
        interested_users = listing.likes.all()
        change_text = ', '.join([f"{k} changed" for k in changes.keys()])
        
        for user in interested_users:
            NotificationService.create_notification(
                recipient=user,
                notification_type='price_update',
                text=f'The listing {listing.title} has been updated: {change_text}',
                content_object=listing
            ) 