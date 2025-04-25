from django.urls import path
from . import views

urlpatterns = [
    path('', views.notification_list, name='notification-list'),
    path('mark-read/<int:notification_id>/', views.mark_notification_read, name='mark-notification-read'),
    path('mark-all-read/', views.mark_all_notifications_read, name='mark-all-notifications-read'),
    path('unread-count/', views.get_unread_count, name='notification-unread-count'),
    path('register-device/', views.register_device, name='register-device'),
    path('unregister-device/', views.unregister_device, name='unregister-device'),
]
