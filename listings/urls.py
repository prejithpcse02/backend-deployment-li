from django.urls import path
from .views import ListingListCreate, ListingDetail, ListingSearch,RecentListings, LikeListing, UserLikes

urlpatterns = [
    path('', ListingListCreate.as_view(), name='listings'),
    path('search/', ListingSearch.as_view(), name='listing-search'),
    path('<slug:slug>/<uuid:product_id>/', ListingDetail.as_view(), name='listing-detail'),
    path('recent/', RecentListings.as_view(), name='recent-listings'),
    path('<slug:slug>/<uuid:product_id>/like/', LikeListing.as_view(), name='like-listing'),
    path('liked/', UserLikes.as_view(), name='user-likes'),
]
