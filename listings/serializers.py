from rest_framework import serializers
from django.conf import settings
from .models import Listing, ListingImage

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

    class Meta:
        model = Listing
        fields = ['id', 'title', 'description', 'price', 'location', 'status', 'created_at', 'seller_name', 'images']
