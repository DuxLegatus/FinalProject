from django.contrib import admin
from .models import Booking,Ticket

# Register your models here.


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ["user", "schedule", "seat", "first_name", "last_name", "status", "booking_time"]
    list_filter = ["status", "schedule__train"]
    search_fields = ["user__username", "first_name", "last_name", "seat__seat_number"]
    list_editable = ["status"]



@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ["ticket_number", "booking", "issued_at"]
    search_fields = ["ticket_number", "booking__user__username"]