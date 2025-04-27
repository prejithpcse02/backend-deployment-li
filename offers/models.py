from django.db import models
from users.models import User
from listings.models import Listing
from model_utils import FieldTracker

class Offer(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="offers")
    offered_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_offers")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20, 
        choices=[("Pending", "Pending"), ("Accepted", "Accepted"), ("Rejected", "Rejected")], 
        default="Pending"
    )
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    tracker = FieldTracker(fields=['status'])

    def __str__(self):
        return f"Offer by {self.offered_by.username} on {self.listing.title} - {self.status}"
