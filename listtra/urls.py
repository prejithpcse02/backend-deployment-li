from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from listings.media_views import MediaServeView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/listings/', include('listings.urls')),  # Keep Listings API
    path('api/', include('users.urls')),  # Keep Users API
    path('api/reviews/', include('reviews.urls')),
    path('api/offers/', include('offers.urls')),
    path('api/chat/', include('chat.urls')),
    path('api/notifications_new/', include('notifications_new.urls')),  # Add new notifications URLs
    
    # JWT Authentication
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('media/<path:path>', MediaServeView.as_view(), name='media'),
]

# Add media URL in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
