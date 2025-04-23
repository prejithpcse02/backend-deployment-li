from rest_framework import serializers
from .models import Conversation, Message
from users.serializers import UserSerializer
from listings.serializers import ListingSerializer
from offers.serializers import OfferSerializer
from offers.models import Offer

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    sender_id = serializers.IntegerField(write_only=True)
    conversation = serializers.PrimaryKeyRelatedField(queryset=Conversation.objects.all())
    offer_id = serializers.IntegerField(required=False, allow_null=True)
    offer = OfferSerializer(read_only=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    listing_title = serializers.CharField(source='conversation.listing.title', read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'conversation', 'sender', 'sender_id', 'content', 'message_type', 'file_url', 
                 'is_read', 'created_at', 'updated_at', 'is_deleted', 'is_offer', 'offer_id', 'offer', 
                 'price', 'listing_title']
        read_only_fields = ['sender', 'created_at', 'updated_at', 'offer', 'listing_title']

    def validate(self, data):
        request = self.context.get('request')
        if request and request.user:
            conversation = data.get('conversation')
            if conversation and request.user not in conversation.participants.all():
                raise serializers.ValidationError("You are not a participant in this conversation")
            
            # Validate offer data if this is an offer message
            if data.get('is_offer'):
                if not data.get('price') and not data.get('offer_id'):
                    raise serializers.ValidationError("Either price or offer_id is required for offer messages")
                
                if data.get('offer_id'):
                    try:
                        offer = Offer.objects.get(id=data['offer_id'])
                        if offer.offered_by != request.user:
                            raise serializers.ValidationError("You can only use your own offers")
                        if offer.status != 'Pending':
                            raise serializers.ValidationError("Can only use pending offers")
                        if offer.listing != conversation.listing:
                            raise serializers.ValidationError("Offer must be for the current listing")
                    except Offer.DoesNotExist:
                        raise serializers.ValidationError("Offer not found")
                
                if data.get('price'):
                    if float(data['price']) <= 0:
                        raise serializers.ValidationError("Offer price must be greater than 0")
                    
                    # Check if user already has a pending offer on this listing
                    existing_offer = Offer.objects.filter(
                        listing=conversation.listing,
                        offered_by=request.user,
                        status='Pending'
                    ).exists()
                    if existing_offer:
                        raise serializers.ValidationError("You already have a pending offer on this listing")
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        price = validated_data.pop('price', None)
        offer_id = validated_data.pop('offer_id', None)
        
        # Create or get offer if this is an offer message
        offer = None
        if validated_data.get('is_offer'):
            if offer_id:
                offer = Offer.objects.get(id=offer_id)
            else:
                conversation = validated_data['conversation']
                offer = Offer.objects.create(
                    listing=conversation.listing,
                    offered_by=request.user,
                    price=price,
                    status='Pending',
                    message=validated_data.get('content', '')
                )
        
        # Create message
        message = Message.objects.create(
            **validated_data,
            offer=offer
        )
        return message

class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    listing = ListingSerializer(read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    other_participant = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['id', 'listing', 'participants', 'last_message', 'unread_count', 
                 'created_at', 'updated_at', 'is_active', 'other_participant']
        read_only_fields = ['created_at', 'updated_at']

    def get_last_message(self, obj):
        last_message = obj.messages.filter(is_deleted=False).last()
        if last_message:
            return MessageSerializer(last_message).data
        return None

    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.messages.filter(is_read=False, is_deleted=False).exclude(sender=request.user).count()
        return 0

    def get_other_participant(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            other_participant = obj.participants.exclude(id=request.user.id).first()
            if other_participant:
                return UserSerializer(other_participant).data
        return None 