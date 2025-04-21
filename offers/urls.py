from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OfferViewSet

router = DefaultRouter()
router.register(r'', OfferViewSet, basename='offer')

urlpatterns = [
    path('', include(router.urls)),
    path('<int:pk>/accept/', OfferViewSet.as_view({'post': 'accept'}), name='offer-accept'),
    path('<int:pk>/reject/', OfferViewSet.as_view({'post': 'reject'}), name='offer-reject'),
]
