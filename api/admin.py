from django.contrib import admin
from .models import (
    Destination, TrekRoute, WeatherCache,
    ChatRoom, ChatMessage, Booking, Review
)


@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'altitude', 'difficulty', 'price', 'featured']
    list_filter = ['difficulty', 'featured', 'best_season']
    search_fields = ['name', 'location', 'description']
    list_editable = ['featured']


@admin.register(TrekRoute)
class TrekRouteAdmin(admin.ModelAdmin):
    list_display = ['destination', 'sequence_order', 'location_name', 'altitude']
    list_filter = ['destination']
    ordering = ['destination', 'sequence_order']


@admin.register(WeatherCache)
class WeatherCacheAdmin(admin.ModelAdmin):
    list_display = ['destination', 'temperature', 'weather_condition', 'risk_level', 'cached_at']
    list_filter = ['risk_level', 'has_rain_warning', 'has_snow_warning']


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ['destination', 'created_at']


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['user', 'chat_room', 'timestamp', 'message']
    list_filter = ['chat_room', 'timestamp']
    search_fields = ['message', 'user__username']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['user', 'destination', 'start_date', 'number_of_people', 'status']
    list_filter = ['status', 'start_date']
    search_fields = ['user__username', 'destination__name']
    list_editable = ['status']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'destination', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__username', 'destination__name', 'comment']
