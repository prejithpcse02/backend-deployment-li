from django.urls import path
from . import views

urlpatterns = [
    path('', views.create_review, name='create-review'),
    path('my-reviews/', views.get_user_reviews, name='get-user-reviews'),
    path('seller/<str:seller_id>/', views.get_seller_reviews, name='get-seller-reviews'),
    path('listing/<uuid:product_id>/', views.get_listing_reviews, name='get-listing-reviews'),
    path('seller/<str:user_id>/summary/', views.seller_rating_summary, name='seller-rating-summary'),
]
