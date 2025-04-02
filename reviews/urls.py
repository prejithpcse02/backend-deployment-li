from django.urls import path
from .views import ReviewListCreate, ReviewDetail

urlpatterns = [
    path('', ReviewListCreate.as_view(), name='review-list'),
    path('<int:pk>/', ReviewDetail.as_view(), name='review-detail'),
]
