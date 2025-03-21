from rest_framework import generics
from .models import Listing
from .serializers import ListingSerializer

class ListingListCreate(generics.ListCreateAPIView):
    """ API to list all listings and create a new listing """
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer

class ListingDetail(generics.RetrieveUpdateDestroyAPIView):
    """ API to retrieve, update, or delete a listing """
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
