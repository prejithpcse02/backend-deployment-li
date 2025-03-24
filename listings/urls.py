from django.urls import path
from .views import ListingListCreate, ListingDetail

urlpatterns = [
    path('', ListingListCreate.as_view(), name='listings'),
    path('<int:pk>/', ListingDetail.as_view(), name='listing-detail'),
]
