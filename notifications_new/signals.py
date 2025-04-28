from django.db.models.signals import post_save
from django.dispatch import receiver
from chat.models import Message
from listings.models import Listing, Like
from offers.models import Offer
from reviews.models import Review
from .services import NotificationService

@receiver(post_save, sender=Message)
def create_message_notification(sender, instance, created, **kwargs):
    """
    Create a notification when a new message is created
    """
    if created and not instance.is_offer:  # Skip notifications for offer messages
        NotificationService.create_new_message_notification(instance)

@receiver(post_save, sender=Listing)
def create_new_listing_notification(sender, instance, created, **kwargs):
    """
    Create notifications when a new listing is created
    """
    if created:
        NotificationService.create_new_listing_notification(instance)

@receiver(post_save, sender=Listing)
def create_listing_sold_notification(sender, instance, created, **kwargs):
    """
    Create notification when a listing is marked as sold
    """
    if not created and instance.status == 'sold':
        # Get the buyer from the most recent accepted offer
        try:
            accepted_offer = Offer.objects.filter(
                listing=instance,
                status='accepted'
            ).latest('created_at')
            
            if accepted_offer:
                NotificationService.create_listing_sold_notification(
                    listing=instance,
                    buyer=accepted_offer.offered_by
                )
        except Offer.DoesNotExist:
            pass

@receiver(post_save, sender=Like)
def create_like_notification(sender, instance, created, **kwargs):
    """
    Create notification when someone likes a listing
    """
    if created:
        NotificationService.create_listing_liked_notification(instance.listing, instance.user)

@receiver(post_save, sender=Offer)
def create_offer_notification(sender, instance, created, **kwargs):
    """
    Create notification for new offer
    """
    if created:
        NotificationService.create_offer_notification(instance)

@receiver(post_save, sender=Offer)
def create_offer_status_notification(sender, instance, **kwargs):
    """
    Create notification when offer status changes
    """
    try:
        if hasattr(instance, 'tracker') and instance.tracker.has_changed('status'):
            if instance.status == 'Accepted':
                NotificationService.create_offer_accepted_notification(instance)
            elif instance.status == 'Rejected':
                NotificationService.create_offer_rejected_notification(instance)
    except Exception as e:
        print(f"Error creating offer status notification: {e}")

@receiver(post_save, sender=Review)
def create_review_notification(sender, instance, created, **kwargs):
    """
    Create notification for new review
    """
    if created:
        NotificationService.create_review_notification(instance) 