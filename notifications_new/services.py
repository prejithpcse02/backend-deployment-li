from django.contrib.contenttypes.models import ContentType
from listings.models import Listing
from .models import Notification
from .utils import send_push_notification

class NotificationService:
    @classmethod
    def create_notification(cls, recipient, notification_type, content_object, message=None, sender=None):
        """
        Generic method to create a notification
        """
        # Get the content type for the object
        content_type = ContentType.objects.get_for_model(content_object)
        
        # Get the object ID based on the model type
        if isinstance(content_object, Listing):
            # For Listing model, use the product_id field
            object_id = content_object.product_id
        else:
            # For other models, use the id field
            object_id = content_object.id
        
        # Create the notification
        notification = Notification.objects.create(
            recipient=recipient,
            notification_type=notification_type,
            content_type=content_type,
            object_id=object_id,
            text=message,
            sender=sender
        )
        
        return notification

    @staticmethod
    def create_new_message_notification(chat_message):
        """
        Create notification for new chat message
        """
        recipient = chat_message.conversation.participants.exclude(id=chat_message.sender.id).first()
        if recipient:
            # Get sender's details
            sender = chat_message.sender
            sender_details = {
                'id': sender.id,
                'username': sender.username,
                'nickname': sender.nickname,
                'email': sender.email,
                'profile_picture': sender.profile_picture.url if hasattr(sender, 'profile_picture') and sender.profile_picture else None
            }
            
            NotificationService.create_notification(
                recipient=recipient,
                notification_type='message',
                text=f'You have a new message from {sender.nickname}',
                sender=sender,
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
                text=f'{listing.seller.nickname} has listed a new item: {listing.title}',
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
                content_object=listing,
                message=f'{liker.nickname} liked your listing: {listing.title}',
                sender=liker
            )

    @staticmethod
    def create_listing_sold_notification(listing, buyer):
        """
        Create notification when a listing is sold
        """
        NotificationService.create_notification(
            recipient=listing.seller,
            notification_type='item_sold',
            text=f'Your listing {listing.title} has been sold to {buyer.nickname}',
            sender=buyer,
            content_object=listing
        )

    @staticmethod
    def create_offer_notification(offer):
        """
        Create notification for new offer
        """
        NotificationService.create_notification(
            recipient=offer.listing.seller,
            notification_type='offer',
            text=f'{offer.user.nickname} made an offer of ₹{offer.amount} on your listing: {offer.listing.title}',
            sender=offer.user,
            content_object=offer
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
            sender=offer.listing.seller,
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
            sender=offer.listing.seller,
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
            text=f'{review.reviewer.nickname} left you a {review.rating}-star review',
            sender=review.reviewer,
            content_object=review
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