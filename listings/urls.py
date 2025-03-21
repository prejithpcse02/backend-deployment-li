from django.urls import path
from . import views
from . import api_views

urlpatterns = [
    # Template-based views
    path('create/', views.create_listing, name='create_listing'),
    path('edit/<int:listing_id>/', views.edit_listing, name='edit_listing'),

    # REST API Endpoints
    path('api/listings/', api_views.ListingListCreate.as_view(), name='api_listings'),
    path('api/listings/<int:pk>/', api_views.ListingDetail.as_view(), name='api_listing_detail'),
]
