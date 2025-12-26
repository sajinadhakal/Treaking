from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.utils import timezone
import requests
from django.conf import settings

from .models import (
    Destination, TrekRoute, WeatherCache,
    ChatRoom, ChatMessage, Booking, Review
)
from .serializers import (
    UserSerializer, UserRegistrationSerializer,
    DestinationListSerializer, DestinationDetailSerializer,
    TrekRouteSerializer, WeatherCacheSerializer,
    ChatRoomSerializer, ChatMessageSerializer,
    BookingSerializer, ReviewSerializer
)


# Authentication Views
@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """Register a new user"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """Login user and return token"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
    if user:
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key
        })
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    """Logout user by deleting token"""
    request.user.auth_token.delete()
    return Response({'message': 'Successfully logged out'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    """Get current user profile"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


# Destination Views
class DestinationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing destinations
    list: Get all destinations
    retrieve: Get single destination with full details
    """
    queryset = Destination.objects.all()
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'location', 'description']
    ordering_fields = ['price', 'duration_days', 'altitude', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return DestinationListSerializer
        return DestinationDetailSerializer
    
    @action(detail=True, methods=['get'])
    def route(self, request, pk=None):
        """Get route coordinates for a destination"""
        destination = self.get_object()
        route_points = destination.route_points.all()
        serializer = TrekRouteSerializer(route_points, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def weather(self, request, pk=None):
        """Get weather data for a destination"""
        destination = self.get_object()
        
        # Check for cached weather data
        cached_weather = destination.weather_data.first()
        if cached_weather and cached_weather.is_cache_valid(settings.WEATHER_CACHE_DURATION):
            serializer = WeatherCacheSerializer(cached_weather)
            return Response(serializer.data)
        
        # Fetch new weather data
        weather_data = fetch_weather_for_destination(destination)
        if weather_data:
            serializer = WeatherCacheSerializer(weather_data)
            return Response(serializer.data)
        
        return Response({'error': 'Unable to fetch weather data'}, 
                       status=status.HTTP_503_SERVICE_UNAVAILABLE)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured destinations"""
        featured = self.queryset.filter(featured=True)
        serializer = self.get_serializer(featured, many=True)
        return Response(serializer.data)


def fetch_weather_for_destination(destination):
    """
    Fetch weather data from OpenWeatherMap API and cache it
    """
    if not settings.WEATHER_API_KEY:
        # Create dummy weather data for development
        return create_dummy_weather(destination)
    
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather"
        params = {
            'lat': destination.latitude,
            'lon': destination.longitude,
            'appid': settings.WEATHER_API_KEY,
            'units': 'metric'
        }
        
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        # Determine risk warnings
        temp = data['main']['temp']
        weather_main = data['weather'][0]['main'].lower()
        
        has_rain = 'rain' in weather_main or 'drizzle' in weather_main
        has_snow = 'snow' in weather_main
        has_altitude_warning = destination.altitude > 4000
        
        # Calculate risk level
        risk_level = 'LOW'
        if has_snow or (has_altitude_warning and temp < 0):
            risk_level = 'HIGH'
        elif has_rain or has_altitude_warning:
            risk_level = 'MEDIUM'
        
        # Delete old cache and create new
        WeatherCache.objects.filter(destination=destination).delete()
        weather_cache = WeatherCache.objects.create(
            destination=destination,
            temperature=temp,
            weather_condition=data['weather'][0]['main'],
            description=data['weather'][0]['description'],
            humidity=data['main']['humidity'],
            wind_speed=data['wind']['speed'],
            has_rain_warning=has_rain,
            has_snow_warning=has_snow,
            has_altitude_warning=has_altitude_warning,
            risk_level=risk_level
        )
        return weather_cache
    
    except Exception as e:
        print(f"Error fetching weather: {e}")
        return create_dummy_weather(destination)


def create_dummy_weather(destination):
    """Create dummy weather data for development"""
    WeatherCache.objects.filter(destination=destination).delete()
    
    has_altitude_warning = destination.altitude > 4000
    weather_cache = WeatherCache.objects.create(
        destination=destination,
        temperature=15.5,
        weather_condition='Clear',
        description='clear sky',
        humidity=65,
        wind_speed=3.5,
        has_rain_warning=False,
        has_snow_warning=False,
        has_altitude_warning=has_altitude_warning,
        risk_level='MEDIUM' if has_altitude_warning else 'LOW'
    )
    return weather_cache


# Chat Views
class ChatRoomViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for chat rooms
    """
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Get messages for a chat room"""
        chat_room = self.get_object()
        messages = chat_room.messages.all()[:100]  # Last 100 messages
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """Send a message to chat room"""
        chat_room = self.get_object()
        message_text = request.data.get('message')
        
        if not message_text:
            return Response({'error': 'Message cannot be empty'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        message = ChatMessage.objects.create(
            chat_room=chat_room,
            user=request.user,
            message=message_text
        )
        
        serializer = ChatMessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_chat_by_destination(request, destination_id):
    """Get or create chat room for a destination"""
    destination = get_object_or_404(Destination, pk=destination_id)
    chat_room, created = ChatRoom.objects.get_or_create(destination=destination)
    serializer = ChatRoomSerializer(chat_room)
    return Response(serializer.data)


# Booking Views
class BookingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for bookings
    """
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# Review Views
class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for reviews
    """
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        destination_id = self.request.query_params.get('destination')
        if destination_id:
            return Review.objects.filter(destination_id=destination_id)
        return Review.objects.all()
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
