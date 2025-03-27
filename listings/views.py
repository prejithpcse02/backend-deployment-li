from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from .models import Listing, Like
from .serializers import ListingSerializer, LikeSerializer
from rest_framework.exceptions import NotFound

class ListingListCreate(generics.ListCreateAPIView):
    """ API to List all Listings and Create a new Listing """
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer

class ListingDetail(generics.RetrieveUpdateDestroyAPIView):
    """ API to Retrieve, Update, or Delete a Listing """
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    lookup_field = 'product_id'
    lookup_url_kwarg = 'product_id'

    def get_object(self):
        slug = self.kwargs.get('slug')
        product_id = self.kwargs.get('product_id')
        
        try:
            return Listing.objects.get(slug=slug, product_id=product_id)
        except Listing.DoesNotExist:
            raise NotFound("Listing not found")


class ListingSearch(generics.ListAPIView):
    serializer_class = ListingSerializer

    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        if query:
            return Listing.objects.filter(
                Q(slug__icontains=query) |
                Q(title__icontains=query) 
    )
        return Listing.objects.none()
    
class RecentListings(generics.ListAPIView):
    """ API to get recently added listings """
    serializer_class = ListingSerializer
    
    def get_queryset(self):
        return Listing.objects.all().order_by('-created_at')[:12]  # Get 12 most recent listings

class LikeListing(generics.CreateAPIView, generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LikeSerializer

    def create(self, request, *args, **kwargs):
        listing_id = kwargs.get('product_id')
        try:
            listing = Listing.objects.get(product_id=listing_id)
            like, created = Like.objects.get_or_create(
                user=request.user,
                listing=listing
            )
            return Response({'status': 'success'})
        except Listing.DoesNotExist:
            return Response(
                {'error': 'Listing not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request, *args, **kwargs):
        listing_id = kwargs.get('product_id')
        try:
            listing = Listing.objects.get(product_id=listing_id)
            Like.objects.filter(user=request.user, listing=listing).delete()
            return Response({'status': 'success'})
        except Listing.DoesNotExist:
            return Response(
                {'error': 'Listing not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
class UserLikes(generics.ListAPIView):
    """ API to get all listings liked by the current user """
    permission_classes = [IsAuthenticated]
    serializer_class = ListingSerializer

    def get_queryset(self):
        return Listing.objects.filter(likes__user=self.request.user)
