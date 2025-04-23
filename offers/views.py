from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Offer
from .serializers import OfferSerializer
from chat.models import Message
import logging

logger = logging.getLogger(__name__)

class OfferViewSet(viewsets.ModelViewSet):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Offer.objects.filter(
            offered_by=user
        ) | Offer.objects.filter(
            listing__seller=user
        )

    def perform_create(self, serializer):
        serializer.save(offered_by=self.request.user)

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        logger.info(f"Accepting offer {pk}")
        offer = self.get_object()
        
        # Check if user is the seller
        if request.user != offer.listing.seller:
            logger.warning(f"User {request.user.id} attempted to accept offer {pk} but is not the seller")
            return Response(
                {"error": "Only the listing owner can accept offers"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if offer is pending
        if offer.status != 'Pending':
            logger.warning(f"Attempted to accept non-pending offer {pk}")
            return Response(
                {"error": "Can only accept pending offers"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update offer status
        offer.status = 'Accepted'
        offer.save()

        # Create a message in the conversation
        conversation = offer.listing.conversations.filter(
            participants=offer.offered_by
        ).first()
        
        if conversation:
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=f"I have accepted your offer of ₹{offer.price}",
                is_offer=True,
                offer=offer
            )

        logger.info(f"Offer {pk} accepted successfully")
        return Response({"status": "offer accepted"})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        logger.info(f"Rejecting offer {pk}")
        offer = self.get_object()
        
        # Check if user is the seller
        if request.user != offer.listing.seller:
            logger.warning(f"User {request.user.id} attempted to reject offer {pk} but is not the seller")
            return Response(
                {"error": "Only the listing owner can reject offers"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if offer is pending
        if offer.status != 'Pending':
            logger.warning(f"Attempted to reject non-pending offer {pk}")
            return Response(
                {"error": "Can only reject pending offers"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update offer status
        offer.status = 'Rejected'
        offer.save()

        # Create a message in the conversation
        conversation = offer.listing.conversations.filter(
            participants=offer.offered_by
        ).first()
        
        if conversation:
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=f"I have rejected your offer of ₹{offer.price}",
                is_offer=True,
                offer=offer
            )

        logger.info(f"Offer {pk} rejected successfully")
        return Response({"status": "offer rejected"})

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        logger.info(f"Cancelling offer {pk}")
        offer = self.get_object()
        
        # Check if user is the one who made the offer
        if request.user != offer.offered_by:
            logger.warning(f"User {request.user.id} attempted to cancel offer {pk} but is not the offer creator")
            return Response(
                {"error": "Only the person who made the offer can cancel it"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if offer is pending
        if offer.status != 'Pending':
            logger.warning(f"Attempted to cancel non-pending offer {pk}")
            return Response(
                {"error": "Can only cancel pending offers"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update offer status
        offer.status = 'Cancelled'
        offer.save()

        # Create a message in the conversation
        conversation = offer.listing.conversations.filter(
            participants=offer.offered_by
        ).first()
        
        if conversation:
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=f"I have cancelled my offer of ₹{offer.price}",
                is_offer=True,
                offer=offer
            )

        logger.info(f"Offer {pk} cancelled successfully")
        return Response({"status": "offer cancelled"})
