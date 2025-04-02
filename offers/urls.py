from django.urls import path
from .views import OfferListCreate, OfferDetail

urlpatterns = [
    path('', OfferListCreate.as_view(), name='offer-list'),
    path('<int:pk>/', OfferDetail.as_view(), name='offer-detail'),
]
