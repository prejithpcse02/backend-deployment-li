from rest_framework import serializers
from .models import Review

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
