from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Review
from .serializers import ReviewSerializer
from django.db.models import Avg, Count
from chat.models import Conversation, Message
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_review(request):
    """
    Create a new review.
    """
    logger.info(f"Received review data: {request.data}")
    
    # Extract data from request
    reviewed_user_id = request.data.get('reviewed_user')
    reviewed_product_id = request.data.get('reviewed_product')
    rating = request.data.get('rating')
    review_text = request.data.get('review_text')
    
    # Validate required fields
    if not reviewed_user_id or not reviewed_product_id or not rating:
        return Response(
            {"error": "Missing required fields: reviewed_user, reviewed_product, rating"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Check for duplicate review
        if Review.objects.filter(
            reviewer=request.user,
            reviewed_user_id=reviewed_user_id,
            reviewed_product_id=reviewed_product_id
        ).exists():
            return Response(
                {"error": "You have already reviewed this seller for this product."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create the review
        review = Review.objects.create(
            reviewer=request.user,
            reviewed_user_id=reviewed_user_id,
            reviewed_product_id=reviewed_product_id,
            rating=rating,
            review_text=review_text
        )
        
        # Find the conversation between buyer and seller
        conversation = Conversation.objects.filter(
            listing__product_id=reviewed_product_id,
            participants=request.user
        ).filter(
            participants=reviewed_user_id
        ).first()
        
        if conversation:
            # Create review notification message
            review_message = f"{request.user.nickname} left a review: {rating} ★{' - ' + review_text if review_text else ''}"
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=review_message,
                message_type="text",
                is_offer=False
            )
            
            # Update conversation timestamp
            conversation.updated_at = timezone.now()
            conversation.save()
        
        # Serialize and return the created review
        serializer = ReviewSerializer(review)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error creating review: {str(e)}")
        return Response(
            {"error": f"Failed to create review: {str(e)}"}, 
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_reviews(request):
    """
    Get all reviews for the authenticated user.
    """
    reviews = Review.objects.filter(reviewer=request.user)
    serializer = ReviewSerializer(reviews, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def seller_rating_summary(request, user_id):
    """
    Get rating summary for a seller.
    """
    try:
        data = Review.objects.filter(reviewed_user_id=user_id).aggregate(
            average=Avg('rating'),
            total=Count('id')
        )
        return Response(data)
    except Exception as e:
        logger.error(f"Error getting seller rating summary: {str(e)}")
        return Response(
            {"error": f"Failed to get seller rating summary: {str(e)}"}, 
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_listing_reviews(request, product_id):
    """
    Get all reviews for a specific listing.
    """
    try:
        reviews = Review.objects.filter(reviewed_product_id=product_id)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)
    except Exception as e:
        logger.error(f"Error fetching listing reviews: {str(e)}")
        return Response(
            {"error": f"Failed to fetch reviews: {str(e)}"}, 
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_seller_reviews(request, seller_id):
    """
    Get all reviews received by a seller.
    """
    try:
        reviews = Review.objects.filter(reviewed_user_id=seller_id)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)
    except Exception as e:
        logger.error(f"Error fetching seller reviews: {str(e)}")
        return Response(
            {"error": f"Failed to fetch reviews: {str(e)}"}, 
            status=status.HTTP_400_BAD_REQUEST
        )