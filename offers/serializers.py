from rest_framework import serializers
from .models import Offer

class OfferSerializer(serializers.ModelSerializer):
    offered_by_username = serializers.CharField(source="offered_by.username", read_only=True)
    
    class Meta:
        model = Offer
        fields = ['id', 'listing', 'offered_by', 'price', 'status', 'message', 'created_at', 'offered_by_username']
        read_only_fields = ['id', 'created_at', 'offered_by']
