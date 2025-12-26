from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import math


class Destination(models.Model):
    """
    Represents a trekking destination (e.g., Annapurna Base Camp, Everest Base Camp)
    """
    DIFFICULTY_CHOICES = [
        ('EASY', 'Easy'),
        ('MODERATE', 'Moderate'),
        ('CHALLENGING', 'Challenging'),
        ('DIFFICULT', 'Difficult'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200)
    altitude = models.IntegerField(help_text="Altitude in meters")
    duration_days = models.IntegerField(help_text="Trek duration in days")
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price in USD")
    image = models.ImageField(upload_to='destinations/', blank=True, null=True)
    featured = models.BooleanField(default=False)
    best_season = models.CharField(max_length=100, blank=True)
    group_size_max = models.IntegerField(default=15)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Coordinates for map center
    latitude = models.FloatField(default=28.0)
    longitude = models.FloatField(default=84.0)
    
    class Meta:
        ordering = ['-featured', 'name']
    
    def __str__(self):
        return self.name


class TrekRoute(models.Model):
    """
    Stores GPS coordinates for trekking routes
    """
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='route_points')
    sequence_order = models.IntegerField(help_text="Order of this point in the route")
    latitude = models.FloatField()
    longitude = models.FloatField()
    altitude = models.IntegerField(help_text="Altitude at this point in meters")
    location_name = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['destination', 'sequence_order']
        unique_together = ['destination', 'sequence_order']
    
    def __str__(self):
        return f"{self.destination.name} - Point {self.sequence_order}"
    
    @staticmethod
    def calculate_distance(lat1, lon1, lat2, lon2):
        """
        Calculate distance between two points using Haversine formula
        Returns distance in kilometers
        """
        R = 6371  # Earth's radius in kilometers
        
        # Convert degrees to radians
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        # Haversine formula
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon / 2) ** 2)
        c = 2 * math.asin(math.sqrt(a))
        
        distance = R * c
        return distance


class WeatherCache(models.Model):
    """
    Caches weather data to reduce API calls
    """
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='weather_data')
    temperature = models.FloatField()
    weather_condition = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    humidity = models.IntegerField()
    wind_speed = models.FloatField()
    
    # Risk indicators
    has_rain_warning = models.BooleanField(default=False)
    has_snow_warning = models.BooleanField(default=False)
    has_altitude_warning = models.BooleanField(default=False)
    risk_level = models.CharField(max_length=20, default='LOW')  # LOW, MEDIUM, HIGH
    
    cached_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-cached_at']
    
    def __str__(self):
        return f"{self.destination.name} - {self.weather_condition}"
    
    def is_cache_valid(self, cache_duration=3600):
        """Check if cache is still valid (default 1 hour)"""
        from django.utils import timezone
        import datetime
        time_diff = timezone.now() - self.cached_at
        return time_diff.total_seconds() < cache_duration


class ChatRoom(models.Model):
    """
    One chat room per destination for group discussions
    """
    destination = models.OneToOneField(Destination, on_delete=models.CASCADE, related_name='chat_room')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['destination__name']
    
    def __str__(self):
        return f"Chat: {self.destination.name}"


class ChatMessage(models.Model):
    """
    Messages in destination-based group chats
    """
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_messages')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    edited = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.user.username} - {self.chat_room.destination.name} - {self.timestamp}"


class Booking(models.Model):
    """
    Booking/Inquiry system for trek packages
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
        ('COMPLETED', 'Completed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='bookings')
    start_date = models.DateField()
    number_of_people = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    special_requirements = models.TextField(blank=True)
    contact_phone = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.destination.name} - {self.start_date}"


class Review(models.Model):
    """
    User reviews for destinations
    """
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['destination', 'user']
    
    def __str__(self):
        return f"{self.user.username} - {self.destination.name} - {self.rating}★"
