"""from django.shortcuts import render, get_object_or_404,redirect
from .models import Listing, ListingImage
from .forms import ListingForm

def create_listing(request):
    if request.method == "POST":
        form = ListingForm(request.POST)
        images = request.FILES.getlist('images')  # Get multiple images
        if form.is_valid():
            listing = form.save()
            for img in images:
                ListingImage.objects.create(listing=listing, image=img)
            return redirect('listing_detail', listing_id=listing.id)
    else:
        form = ListingForm()
    return render(request, 'create_listing.html', {'form': form})


def edit_listing(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)
    if request.method == "POST":
        form = ListingForm(request.POST, instance=listing)
        images = request.FILES.getlist('images')
        if form.is_valid():
            form.save()
            for img in images:
                ListingImage.objects.create(listing=listing, image=img)
            return redirect('listing_detail', listing_id=listing.id)
    else:
        form = ListingForm(instance=listing)
    return render(request, 'edit_listing.html', {'form': form, 'listing': listing})"""

from rest_framework import generics
from .models import Listing
from .serializers import ListingSerializer

class ListingListCreate(generics.ListCreateAPIView):
    """ API to List all Listings and Create a new Listing """
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer

class ListingDetail(generics.RetrieveUpdateDestroyAPIView):
    """ API to Retrieve, Update, or Delete a Listing """
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer



