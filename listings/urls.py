from django.urls import path, re_path
from .views import (
    ListingListCreate, 
    ListingDetail, 
    ListingSearch,
    RecentListings,
    LikeListing,
    UserLikes,
    ListingLikeCount,
    ListingCreate
)

urlpatterns = [
    path('', ListingListCreate.as_view(), name='listings'),
    path('search/', ListingSearch.as_view(), name='listing-search'),
    path('create/', ListingCreate.as_view(), name='listing-create'),
    path('recent/', RecentListings.as_view(), name='recent-listings'),
    path('<slug:slug>/<uuid:product_id>/like/', LikeListing.as_view(), name='like-listing'),
    path('liked/', UserLikes.as_view(), name='user-likes'),
    path('<slug:slug>/<uuid:product_id>/like-count/', ListingLikeCount.as_view(), name='listing-like-count'),
    path('<slug:slug>/<uuid:product_id>/', ListingDetail.as_view(), name='listing-detail'),
    path('<uuid:product_id>/', ListingDetail.as_view(), name='listing-detail-by-id'),
    path('<uuid:product_id>/edit/', ListingDetail.as_view(), name='listing-edit'),
]
