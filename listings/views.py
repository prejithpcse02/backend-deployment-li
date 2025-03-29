from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from django.db.models import Q
from .models import Listing, Like, Search
from .serializers import ListingSerializer, LikeSerializer, SearchSerializer
from rest_framework.exceptions import NotFound
from django.shortcuts import get_object_or_404

class ListingListCreate(generics.ListCreateAPIView):
    """ API to List all Listings and Create a new Listing """
    queryset = Listing.objects.all().order_by('-created_at')
    serializer_class = ListingSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

class ListingDetail(generics.RetrieveUpdateDestroyAPIView):
    """ API to Retrieve, Update, or Delete a Listing """
    queryset = Listing.objects.all().order_by('-created_at')
    serializer_class = ListingSerializer
    #authentication_classes = [JWTAuthentication]
    #permission_classes = [IsAuthenticated]
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
    permission_classes = [AllowAny]

    def get_queryset(self):
        query = self.request.query_params.get('query', '')
        if query:
            return Listing.objects.filter(
                Q(slug__icontains=query) |
                Q(title__icontains=query) 
            )
        return Listing.objects.none()

"""class ListingSearch(generics.ListAPIView):
    serializer_class = ListingSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        query = self.request.query_params.get('query', '')
        if query:
            search_data = {'query' : query}
            if self.request.user.is_authenticated:
                search_data['user'] = self.request.user
            else:
                session_key = self.request.session.session_key
                if not session_key:
                    self.request.session.create()
                    session_key = self.request.session.session_key
                search_data['session_key'] = session_key
            Search.objects.create(**search_data)
            return Listing.objects.filter(
                Q(slug__icontains=query) |
                Q(title__icontains=query) 
    )
        return Listing.objects.none()"""
    
class RecentListings(generics.ListAPIView):
    """ API to get recently added listings """
    serializer_class = ListingSerializer
    
    def get_queryset(self):
        return Listing.objects.all().order_by('-created_at')[:12]  # Get 12 most recent listings
    
"""class RecentSearch(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]
    serializer_class = SearchSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Search.objects.filter(user=self.request.user).order_by('-created_at')[:5]
        else:
            session_key = self.request.session.session_key
            if not session_key:
                self.request.session.create()
                session_key = self.request.session.session_key
            return Search.objects.filter(session_key=session_key).order_by('-created_at')[:5]
        
class AllSearch(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]
    serializer_class = SearchSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Search.objects.filter(user=self.request.user).order_by('-created_at')
        else:
            session_key = self.request.session.session_key
            if not session_key:
                session_key = self.request.session.create()
                session_key = self.request.session.session_key
            return Search.objects.filter(session_key=session_key).order_by('-created_at')"""

class LikeListing(generics.CreateAPIView, generics.DestroyAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = LikeSerializer

    def create(self, request, *args, **kwargs):
        listing_id = kwargs.get('product_id')
        try:
            listing = Listing.objects.get(product_id=listing_id)
            # Check if like already exists
            if Like.objects.filter(user=request.user, listing=listing).exists():
                return Response(
                    {'error': 'You have already liked this listing'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create the like
            like = Like.objects.create(user=request.user, listing=listing)
            serializer = self.get_serializer(like)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Listing.DoesNotExist:
            return Response(
                {'error': 'Listing not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request, *args, **kwargs):
        listing_id = kwargs.get('product_id')
        try:
            listing = Listing.objects.get(product_id=listing_id)
            # Check if like exists
            like = Like.objects.filter(user=request.user, listing=listing)
            if not like.exists():
                return Response(
                    {'error': 'You have not liked this listing'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Delete the like
            like.delete()
            return Response({'status': 'success'}, status=status.HTTP_204_NO_CONTENT)
        except Listing.DoesNotExist:
            return Response(
                {'error': 'Listing not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

class UserLikes(generics.ListAPIView):
    """ API to get all listings liked by the current user """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ListingSerializer

    def get_queryset(self):
        return Listing.objects.filter(likes__user=self.request.user).distinct()

class ListingLikeCount(generics.RetrieveAPIView):
    def get(self, request, slug, product_id):
        listing = get_object_or_404(Listing, slug=slug, product_id=product_id)
        like_count = listing.likes.count()
        return Response({"like_count": like_count}, status=status.HTTP_200_OK)