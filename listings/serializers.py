from rest_framework import serializers
from django.conf import settings
from .models import Listing, ListingImage, Like, Search

class ListingImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ListingImage
        fields = ['id', 'image_url']  # ✅ Only return image URL

    def get_image_url(self, obj):
        """ ✅ Ensure full image URL is returned """
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None

class ListingSerializer(serializers.ModelSerializer):
    seller_name = serializers.CharField(source='seller.nickname', read_only=True)  # ✅ Include seller name
    images = ListingImageSerializer(many=True, read_only=True)  # ✅ Return images as a list of URLs
    is_liked = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Listing
        fields = ['product_id', 'title', 'slug', 'description', 'price', 'condition', 
                 'location', 'status', 'created_at', 'seller_name', 'images',
                 'is_liked', 'likes_count']

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if not request or not request.user or not request.user.is_authenticated:
            return False
        return obj.likes.filter(user=request.user).exists()

    def get_likes_count(self, obj):
        return obj.likes.count()


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'user', 'listing']
        read_only_fields = ['user']

class SearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Search
        fields = ['query','user','created_at']