from rest_framework import serializers
from .models import Review
from users.models import User
from listings.models import Listing
import logging

logger = logging.getLogger(__name__)

class ReviewSerializer(serializers.ModelSerializer):
    reviewer_username = serializers.CharField(source="reviewer.username", read_only=True)
    reviewed_username = serializers.CharField(source="reviewed_user.username", read_only=True)

    class Meta:
        model = Review
        fields = [
            'id', 'reviewer', 'reviewed_user', 'reviewed_product', 'rating', 'review_text', 
            'product_image', 'parent_review', 'created_at', 'reviewer_username', 'reviewed_username'
        ]
        read_only_fields = ['id', 'created_at', 'reviewer']

    def validate_reviewed_user(self, value):
        logger.info(f"Validating reviewed_user: {value}")
        try:
            # If value is an ID, get the user
            if isinstance(value, int):
                user = User.objects.get(id=value)
                return user
            # If value is already a user object, return it
            elif isinstance(value, User):
                return value
            else:
                raise serializers.ValidationError(f"Invalid user ID: {value}")
        except User.DoesNotExist:
            logger.error(f"User not found: {value}")
            raise serializers.ValidationError(f"User with ID {value} not found")

    def validate_reviewed_product(self, value):
        logger.info(f"Validating reviewed_product: {value}")
        try:
            # If value is an ID, get the listing
            if isinstance(value, int):
                listing = Listing.objects.get(id=value)
                return listing
            # If value is already a listing object, return it
            elif isinstance(value, Listing):
                return value
            else:
                raise serializers.ValidationError(f"Invalid listing ID: {value}")
        except Listing.DoesNotExist:
            logger.error(f"Listing not found: {value}")
            raise serializers.ValidationError(f"Listing with ID {value} not found")

    def validate_rating(self, value):
        logger.info(f"Validating rating: {value}")
        if not isinstance(value, int) or value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be an integer between 1 and 5")
        return value
