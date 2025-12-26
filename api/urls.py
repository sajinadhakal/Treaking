from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'destinations', views.DestinationViewSet, basename='destination')
router.register(r'chatrooms', views.ChatRoomViewSet, basename='chatroom')
router.register(r'bookings', views.BookingViewSet, basename='booking')
router.register(r'reviews', views.ReviewViewSet, basename='review')

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', views.register_user, name='register'),
    path('auth/login/', views.login_user, name='login'),
    path('auth/logout/', views.logout_user, name='logout'),
    path('auth/profile/', views.get_user_profile, name='profile'),
    
    # Chat endpoint
    path('chat/destination/<int:destination_id>/', views.get_chat_by_destination, name='chat-by-destination'),
    
    # Router URLs
    path('', include(router.urls)),
]
