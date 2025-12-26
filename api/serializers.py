from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Destination, TrekRoute, WeatherCache, 
    ChatRoom, ChatMessage, Booking, Review
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name']
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords do not match")
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        # Django uses PBKDF2 with SHA256 for password hashing (secure)
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user


class TrekRouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrekRoute
        fields = ['id', 'sequence_order', 'latitude', 'longitude', 
                 'altitude', 'location_name', 'description']


class WeatherCacheSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherCache
        fields = ['id', 'temperature', 'weather_condition', 'description',
                 'humidity', 'wind_speed', 'has_rain_warning', 'has_snow_warning',
                 'has_altitude_warning', 'risk_level', 'cached_at']


class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'user', 'rating', 'comment', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class DestinationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list view"""
    class Meta:
        model = Destination
        fields = ['id', 'name', 'location', 'altitude', 'duration_days',
                 'difficulty', 'price', 'image', 'featured', 'latitude', 'longitude']


class DestinationDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer with all related data"""
    route_points = TrekRouteSerializer(many=True, read_only=True)
    weather_data = WeatherCacheSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    total_reviews = serializers.SerializerMethodField()
    
    class Meta:
        model = Destination
        fields = '__all__'
    
    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews:
            return sum(r.rating for r in reviews) / len(reviews)
        return 0
    
    def get_total_reviews(self, obj):
        return obj.reviews.count()


class ChatMessageSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = ChatMessage
        fields = ['id', 'user', 'username', 'message', 'timestamp', 'edited']
        read_only_fields = ['id', 'timestamp', 'edited']


class ChatRoomSerializer(serializers.ModelSerializer):
    destination_name = serializers.CharField(source='destination.name', read_only=True)
    messages = ChatMessageSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatRoom
        fields = ['id', 'destination', 'destination_name', 'messages', 
                 'message_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_message_count(self, obj):
        return obj.messages.count()


class BookingSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    destination_name = serializers.CharField(source='destination.name', read_only=True)
    
    class Meta:
        model = Booking
        fields = ['id', 'user', 'destination', 'destination_name', 'start_date',
                 'number_of_people', 'status', 'special_requirements', 
                 'contact_phone', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'status']
