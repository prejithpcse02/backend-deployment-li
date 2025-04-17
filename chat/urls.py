from django.urls import path
from .views import ConversationViewSet, MessageViewSet

urlpatterns = [
    # Conversation endpoints
    path('conversations/', ConversationViewSet.as_view({'get': 'list', 'post': 'create'}), name='conversation-list'),
    path('conversations/<int:pk>/', ConversationViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'}), name='conversation-detail'),
    path('conversations/<int:pk>/messages/', ConversationViewSet.as_view({'get': 'messages'}), name='conversation-messages'),
    path('conversations/<int:pk>/archive/', ConversationViewSet.as_view({'post': 'archive'}), name='conversation-archive'),
    
    # Message endpoints
    path('messages/', MessageViewSet.as_view({'get': 'list', 'post': 'create'}), name='message-list'),
    path('messages/<int:pk>/', MessageViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'}), name='message-detail'),
    path('messages/<int:pk>/mark-read/', MessageViewSet.as_view({'post': 'mark_read'}), name='message-mark-read'),
    path('messages/<int:pk>/delete/', MessageViewSet.as_view({'post': 'delete'}), name='message-delete'),
] 