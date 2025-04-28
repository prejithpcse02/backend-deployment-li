from django.contrib.contenttypes.models import ContentType
from listings.models import Listing
from offers.models import Offer
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
            # For Listing model, use the product_id and slug
            object_id = f"{content_object.slug}:{content_object.product_id}"
        elif isinstance(content_object, Offer):
            # For Offer model, use the listing's slug and product_id
            object_id = f"{content_object.listing.slug}:{content_object.listing.product_id}"
        elif hasattr(content_object, 'conversation') and hasattr(content_object.conversation, 'listing'):
            # For messages and offers, use the listing's slug and product_id
            listing = content_object.conversation.listing
            object_id = f"{listing.slug}:{listing.product_id}"
        else:
            # For other models, use the id field
            object_id = str(content_object.id)
        
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
            listing = chat_message.conversation.listing
            
            NotificationService.create_notification(
                recipient=recipient,
                notification_type='message',
                message=f'You have a new message from {sender.nickname}',
                sender=sender,
                content_object=listing  # Pass the listing instead of the message
            )

    @staticmethod
    def create_new_listing_notification(listing):
        """
        Create notification for new listing (for followers)
        """
        try:
            # Check if the seller has followers
            if hasattr(listing.seller, 'followers'):
                followers = listing.seller.followers.all()
                for follower in followers:
                    NotificationService.create_notification(
                        recipient=follower,
                        notification_type='new_listing',
                        message=f'{listing.seller.nickname} has listed a new item: {listing.title}',
                        sender=listing.seller,
                        content_object=listing
                    )
        except Exception as e:
            # Log the error but don't break the listing creation
            print(f"Error creating listing notifications: {str(e)}")

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
            message=f'Your listing {listing.title} has been sold to {buyer.nickname}',
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
            content_object=offer,  # Pass the offer directly
            message=f'{offer.offered_by.nickname} made an offer of ₹{offer.price} on your listing: {offer.listing.title}',
            sender=offer.offered_by
        )

    @staticmethod
    def create_offer_accepted_notification(offer):
        """
        Create notification when an offer is accepted
        """
        NotificationService.create_notification(
            recipient=offer.offered_by,
            notification_type='offer',
            content_object=offer,  # Pass the offer directly
            message=f'Your offer of ₹{offer.price} for {offer.listing.title} has been accepted!',
            sender=offer.listing.seller
        )

    @staticmethod
    def create_offer_rejected_notification(offer):
        """
        Create notification when an offer is rejected
        """
        NotificationService.create_notification(
            recipient=offer.offered_by,
            notification_type='offer',
            content_object=offer,  # Pass the offer directly
            message=f'Your offer of ₹{offer.price} for {offer.listing.title} has been rejected',
            sender=offer.listing.seller
        )

    @staticmethod
    def create_review_notification(review):
        """
        Create notification for new review
        """
        NotificationService.create_notification(
            recipient=review.reviewed_user,
            notification_type='review',
            content_object=review.reviewed_product,  # reviewed_product is already a Listing object
            message=f'{review.reviewer.nickname} left you a {review.rating}-star review',
            sender=review.reviewer
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