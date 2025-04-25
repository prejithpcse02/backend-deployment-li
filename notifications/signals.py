from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from notifications.models import Notification
from notifications.services import NotificationService
from chat.models import Message
from offers.models import Offer
from reviews.models import Review
from listings.models import Listing

@receiver(post_save, sender=Message)
def create_message_notification(sender, instance, created, **kwargs):
    if created:
        # Get the other participant in the conversation
        recipient = instance.conversation.participants.exclude(id=instance.sender.id).first()
        if recipient:
            NotificationService.create_new_message_notification(instance)

@receiver(post_save, sender=Offer)
def create_offer_notification(sender, instance, created, **kwargs):
    if created:
        NotificationService.create_offer_notification(instance)

@receiver(post_save, sender=Offer)
def handle_offer_status_change(sender, instance, **kwargs):
    if instance.tracker.has_changed('status'):
        if instance.status == 'accepted':
            NotificationService.create_offer_accepted_notification(instance)
        elif instance.status == 'rejected':
            NotificationService.create_offer_rejected_notification(instance)

@receiver(post_save, sender=Review)
def create_review_notification(sender, instance, created, **kwargs):
    if created:
        NotificationService.create_review_notification(instance)

@receiver(post_save, sender=Listing)
def create_new_listing_notification(sender, instance, created, **kwargs):
    if created:
        NotificationService.create_new_listing_notification(instance)

@receiver(post_save, sender=Listing)
def handle_listing_updates(sender, instance, **kwargs):
    if instance.tracker.has_changed():
        changes = instance.tracker.changed()
        NotificationService.create_listing_updated_notification(instance, changes)

@receiver(post_save, sender=Listing)
def handle_listing_likes(sender, instance, **kwargs):
    if instance.tracker.has_changed('likes'):
        new_likes = set(instance.likes.all()) - set(instance.tracker.previous('likes'))
        for liker in new_likes:
            NotificationService.create_listing_liked_notification(instance, liker) 