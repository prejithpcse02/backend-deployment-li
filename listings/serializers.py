from rest_framework import serializers
from django.conf import settings
from .models import Listing, ListingImage, Like, Search

class ListingImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    is_primary = serializers.SerializerMethodField()

    class Meta:
        model = ListingImage
        fields = ['id', 'image_url', 'is_primary']  # Include is_primary field

    def get_image_url(self, obj):
        """ ✅ Ensure full image URL is returned """
        request = self.context.get('request')
        if obj.image:
            if settings.DEBUG:
                return request.build_absolute_uri(obj.image.url)
            else:
                return f"{settings.MEDIA_HOST}{obj.image.url}"
        return None
        
    def get_is_primary(self, obj):
        """Handle the case where is_primary field doesn't exist"""
        if hasattr(obj, 'is_primary'):
            return obj.is_primary
        # If is_primary doesn't exist, consider the first image as primary
        if obj.listing.images.exists():
            return obj.listing.images.first().id == obj.id
        return False

class ListingSerializer(serializers.ModelSerializer):
    seller_name = serializers.CharField(source='seller.nickname', read_only=True)  # ✅ Include seller name
    seller_id = serializers.IntegerField(source='seller.id', read_only=True)  # Add seller ID
    images = ListingImageSerializer(many=True, read_only=True)  # ✅ Return images as a list of URLs
    is_liked = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Listing
        fields = ['product_id', 'title', 'slug', 'description', 'price', 'condition', 
                 'location', 'status', 'created_at', 'seller_name', 'seller_id', 'images',
                 'is_liked', 'likes_count']

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if not request or not request.user or not request.user.is_authenticated:
            return False
        return obj.likes.filter(user=request.user).exists()

    def get_likes_count(self, obj):
        return obj.likes.count()
    
class ListingDetailSerializer(serializers.ModelSerializer):
    """Serializer for listing detail view - shows all information"""
    seller_name = serializers.CharField(source='seller.nickname', read_only=True)
    seller_id = serializers.IntegerField(source='seller.id', read_only=True)
    images = ListingImageSerializer(many=True, read_only=True)
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Listing
        fields = ['product_id', 'title', 'description', 'price', 'condition', 
                 'location', 'status', 'seller_name', 'seller_id', 'images',
                 'is_liked', 'likes_count', 'created_at']
        
    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if not request or not request.user or not request.user.is_authenticated:
            return False
        return obj.likes.filter(user=request.user).exists()
    

class ListingCreateSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True
    )
    class Meta:
        model = Listing
        fields = ['title', 'description', 'price','slug', 'condition', 
                 'location', 'images']
        
    def validate_slug(self,value):
        if value:
            if ' ' in value:
                raise serializers.ValidationError("Slug cannot contain spaces")
            return value.lower()
        return value
                
        
    def create(self,validated_data):
        images = validated_data.pop('images')
        listing = Listing.objects.create(**validated_data)
        for image in images:
            ListingImage.objects.create(listing=listing, image=image)
        return listing


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'user', 'listing']
        read_only_fields = ['user']

class SearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Search
        fields = ['query','user','created_at']