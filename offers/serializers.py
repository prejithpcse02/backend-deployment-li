from rest_framework import serializers
from .models import Offer
from listings.models import Listing

class OfferSerializer(serializers.ModelSerializer):
    offered_by_username = serializers.CharField(source="offered_by.username", read_only=True)
    listing_title = serializers.CharField(source="listing.title", read_only=True)
    
    class Meta:
        model = Offer
        fields = ['id', 'listing', 'listing_title', 'offered_by', 'price', 'status', 'message', 'created_at', 'offered_by_username']
        read_only_fields = ['id', 'created_at', 'offered_by', 'status']

    def validate_listing(self, value):
        request = self.context.get('request')
        if request and request.user:
            # Check if listing exists and is active
            try:
                listing = Listing.objects.get(id=value.id)
                if not listing.is_active:
                    raise serializers.ValidationError("This listing is no longer active")
                # Check if user is not the seller
                if listing.seller == request.user:
                    raise serializers.ValidationError("You cannot make an offer on your own listing")
                # Check if listing is not already sold
                if listing.status == 'Sold':
                    raise serializers.ValidationError("This item has already been sold")
            except Listing.DoesNotExist:
                raise serializers.ValidationError("Listing not found")
        return value

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Offer price must be greater than 0")
        return value

    def validate(self, data):
        request = self.context.get('request')
        if request and request.user:
            listing = data.get('listing')
            if listing:
                # Check if user already has a pending offer on this listing
                existing_offer = Offer.objects.filter(
                    listing=listing,
                    offered_by=request.user,
                    status='Pending'
                ).exists()
                if existing_offer:
                    raise serializers.ValidationError("You already have a pending offer on this listing")
        return data
