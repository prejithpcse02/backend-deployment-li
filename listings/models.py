from django.db import models
from users.models import User

class Listing(models.Model):
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('like_new', 'Like New'),
        ('lightly_used', 'Lightly Used'),
        ('well_used', 'Well Used'),
        ('heavily_used', 'Heavily Used'),
    ]

    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='new')
    location = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=[
        ('available', 'Available'),
        ('pending', 'Pending'),
        ('sold', 'Sold'),
    ], default='available')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # Allows editing

    def __str__(self):
        return f"{self.title} - {self.seller.nickname}"

class ListingImage(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to='listing_images/')

    def __str__(self):
        return f"Image for {self.listing.title}"