from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from django.db.models import Q
from .models import Listing, Like, Search, ListingImage
from .serializers import ListingSerializer, LikeSerializer, SearchSerializer,ListingCreateSerializer, ListingDetailSerializer
from rest_framework.exceptions import NotFound
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import MultiPartParser, FormParser

class ListingListCreate(generics.ListCreateAPIView):
    """ API to List all Listings and Create a new Listing """
    queryset = Listing.objects.all().order_by('-created_at')
    serializer_class = ListingSerializer
    #authentication_classes = [JWTAuthentication]
    #permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Listing.objects.all().order_by('-created_at')
        seller_id = self.request.query_params.get('seller', None)
        if seller_id:
            queryset = queryset.filter(seller_id=seller_id)
        return queryset
    
class ListingCreate(generics.CreateAPIView):
    serializer_class = ListingCreateSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

"""class ListingDetail(generics.RetrieveUpdateDestroyAPIView):
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
            raise NotFound("Listing not found")"""

class ListingDetail(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint for retrieving, updating, or deleting a listing"""
    queryset = Listing.objects.all()
    serializer_class = ListingDetailSerializer
    authentication_classes = [JWTAuthentication]
    parser_classes = [MultiPartParser, FormParser]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    lookup_field = 'product_id'
    lookup_url_kwarg = 'product_id'

    def get_object(self):
        slug = self.kwargs.get('slug')
        product_id = self.kwargs.get('product_id')
        
        try:
            if slug:
                # If slug is provided, use both slug and product_id
                return Listing.objects.get(slug=slug, product_id=product_id)
            else:
                # If only product_id is provided, use just that
                return Listing.objects.get(product_id=product_id)
        except Listing.DoesNotExist:
            raise NotFound("Listing not found")
    
    def update(self, request, *args, **kwargs):
        # Get the listing object
        listing = self.get_object()
        
        # Check if user is the owner of the listing
        if request.user.id != listing.seller.id:
            raise PermissionDenied("You don't have permission to edit this listing")
        
        # Log the request data
        print("Update request data:", request.data)
        
        # Handle price field specially to avoid floating point issues
        data = request.data.copy()
        if 'price' in data:
            price_str = data['price']
            print(f"Processing price from request: {price_str}, type: {type(price_str)}")
            
            # If it's a string (which it should be from FormData), try to parse it correctly
            if isinstance(price_str, str):
                try:
                    # Convert to Decimal directly to avoid floating-point issues
                    from decimal import Decimal
                    price_value = Decimal(price_str)
                    print(f"Parsed price value: {price_value}")
                    data['price'] = price_value
                except Exception as e:
                    print(f"Error parsing price: {e}")
        
        # Update basic fields with serializer
        serializer = self.get_serializer(listing, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # Handle image deletions
        if 'images_to_delete' in request.data:
            # Handle JSON array format
            try:
                import json
                images_to_delete = json.loads(request.data['images_to_delete'])
                for image_id in images_to_delete:
                    try:
                        image = ListingImage.objects.get(id=image_id, listing=listing)
                        image.delete()
                        print(f"Deleted image: {image_id}")
                    except ListingImage.DoesNotExist:
                        print(f"Image not found: {image_id}")
            except json.JSONDecodeError:
                # Handle individual fields
                images_to_delete = request.data.getlist('images_to_delete')
                for image_id in images_to_delete:
                    try:
                        image = ListingImage.objects.get(id=image_id, listing=listing)
                        image.delete()
                        print(f"Deleted image: {image_id}")
                    except ListingImage.DoesNotExist:
                        print(f"Image not found: {image_id}")
        
        # Check for alternate format for image deletion
        if 'images_to_delete_list[]' in request.data:
            images_to_delete = request.data.getlist('images_to_delete_list[]')
            for image_id in images_to_delete:
                try:
                    image = ListingImage.objects.get(id=image_id, listing=listing)
                    image.delete()
                    print(f"Deleted image (alt format): {image_id}")
                except ListingImage.DoesNotExist:
                    print(f"Image not found (alt format): {image_id}")
        
        # Handle setting main image for existing images
        if 'main_image_id' in request.data and request.data['main_image_id']:
            main_image_id = request.data['main_image_id']
            try:
                # Set all images to not primary first
                ListingImage.objects.filter(listing=listing).update(is_primary=False)
                
                # Set the selected one to primary
                main_image = ListingImage.objects.get(id=main_image_id, listing=listing)
                main_image.is_primary = True
                main_image.save()
                print(f"Set main image: {main_image_id}")
                
                # Double-check that it was set correctly
                reloaded_image = ListingImage.objects.get(id=main_image_id)
                print(f"Image {main_image_id} is_primary status after save: {reloaded_image.is_primary}")
                
                # Verify no other images are primary
                other_primary = ListingImage.objects.filter(listing=listing, is_primary=True).exclude(id=main_image_id).count()
                if other_primary > 0:
                    print(f"WARNING: Found {other_primary} other primary images - fixing...")
                    ListingImage.objects.filter(listing=listing, is_primary=True).exclude(id=main_image_id).update(is_primary=False)
            except ListingImage.DoesNotExist:
                print(f"Main image not found: {main_image_id}")
                # If the specified image doesn't exist, use the first available image
                first_image = ListingImage.objects.filter(listing=listing).first()
                if first_image:
                    first_image.is_primary = True
                    first_image.save()
                    print(f"Set first available image as main instead: {first_image.id}")
            except Exception as e:
                print(f"Error setting main image: {e}")
        
        # Handle new images
        new_images = []
        
        # Try different ways the images might be sent
        new_image_fields = [k for k in request.data.keys() if k.startswith('new_image_')]
        if new_image_fields:
            # Handle indexed image fields
            for field in new_image_fields:
                if request.FILES.get(field):
                    new_image = ListingImage.objects.create(
                        listing=listing,
                        image=request.FILES[field],
                        is_primary=False  # Not primary by default
                    )
                    new_images.append(new_image)
                    print(f"Added new image from {field}: {new_image.id}")
        elif request.FILES.getlist('new_images'):
            # Handle multiple image uploads with the same field name
            for image_file in request.FILES.getlist('new_images'):
                new_image = ListingImage.objects.create(
                    listing=listing,
                    image=image_file,
                    is_primary=False
                )
                new_images.append(new_image)
                print(f"Added new image from new_images list: {new_image.id}")
        
        # Handle setting main image from new images
        if 'set_main_image_from_new' in request.data and new_images:
            print("Setting a new image as main (primary)")
            # Set all existing images to not primary
            ListingImage.objects.filter(listing=listing).update(is_primary=False)
            # Set the first new image to primary
            new_images[0].is_primary = True
            new_images[0].save()
            print(f"Set first new image as main: {new_images[0].id}")
            
            # Double-check that it was set correctly
            reloaded_image = ListingImage.objects.get(id=new_images[0].id)
            print(f"New image {new_images[0].id} is_primary status after save: {reloaded_image.is_primary}")
        
        # If no image is set as primary, set the first image as primary
        if not ListingImage.objects.filter(listing=listing, is_primary=True).exists() and ListingImage.objects.filter(listing=listing).exists():
            first_image = ListingImage.objects.filter(listing=listing).first()
            first_image.is_primary = True
            first_image.save()
            print(f"Set first existing image as main by default: {first_image.id}")
            
            # Double-check that it was set correctly
            reloaded_image = ListingImage.objects.get(id=first_image.id)
            print(f"Default image {first_image.id} is_primary status after save: {reloaded_image.is_primary}")
            
        # Final check - get all images and their primary status
        all_images = ListingImage.objects.filter(listing=listing)
        print(f"Final image count: {all_images.count()}")
        for img in all_images:
            print(f"Image {img.id}: is_primary={img.is_primary}")
        
        # Ensure at least one image is primary
        primary_count = ListingImage.objects.filter(listing=listing, is_primary=True).count()
        if primary_count == 0 and all_images.count() > 0:
            print("FIXING: No primary images found after all operations!")
            first_image = all_images.first()
            first_image.is_primary = True
            first_image.save()
            print(f"Set image {first_image.id} as primary as fallback")
        elif primary_count > 1:
            print(f"FIXING: Multiple primary images found ({primary_count})")
            # Keep only the first one as primary
            primary_images = ListingImage.objects.filter(listing=listing, is_primary=True)
            first_primary = primary_images.first()
            primary_images.exclude(id=first_primary.id).update(is_primary=False)
            print(f"Kept only {first_primary.id} as primary")
        
        # Return the updated listing
        from rest_framework.response import Response
        updated_listing = self.get_serializer(listing).data
        return Response(updated_listing)
            
    def destroy(self, request, *args, **kwargs):
        # Get the listing object
        listing = self.get_object()
        
        # Check if user is the owner of the listing
        if request.user.id != listing.seller.id:
            raise PermissionDenied("You don't have permission to delete this listing")
            
        # Perform the deletion
        listing.delete()
        
        # Return success response
        from rest_framework.response import Response
        from rest_framework import status
        return Response({"detail": "Listing deleted successfully"}, status=status.HTTP_200_OK)


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