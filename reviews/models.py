from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import User
from listings.models import Listing, ListingImage

class Review(models.Model):
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews_given")
    reviewed_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews_received")
    reviewed_product = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="product_reviews")
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )  # Required field
    review_text = models.TextField(blank=True, null=True)
    product_image = models.ForeignKey(ListingImage, on_delete=models.CASCADE, related_name="review_images", blank=True, null=True)
    parent_review = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name="replies"
    )  # For replies to reviews
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.reviewer.username} for {self.reviewed_user.username}"

