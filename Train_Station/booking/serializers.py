from rest_framework import serializers
from .models import Booking, Ticket
from Train.models import Seat, TrainSchedule
from Train.serializers import SeatSerializer, TrainScheduleSerializer
import uuid

class BookingSerializer(serializers.ModelSerializer):

    seat = SeatSerializer(read_only=True)
    seat_id = serializers.PrimaryKeyRelatedField(
        queryset=Seat.objects.all(),
        write_only=True,
        source="seat"
    )

    schedule = TrainScheduleSerializer(read_only=True)
    schedule_id = serializers.PrimaryKeyRelatedField(
        queryset=TrainSchedule.objects.all(),
        write_only=True,
        source="schedule"
    )

    class Meta:
        model = Booking
        fields = ["id","user","schedule","schedule_id","first_name","last_name","personal_number","email","phone","seat","seat_id","booking_time","status",]
        read_only_fields = ["id","user", "booking_time"]
    
    def create(self, validated_data):

        booking = Booking.objects.create(**validated_data)

        Ticket.objects.create(
            booking=booking,
            train_schedule=booking.schedule,
            ticket_number=str(uuid.uuid4().hex[:16]).upper()
        )

        return booking


class TicketSerializer(serializers.ModelSerializer):
    booking = BookingSerializer(read_only=True)

    class Meta:
        model = Ticket
        fields = ["id","booking","train_schedule","ticket_number","issued_at",]
        read_only_fields = ["id", "ticket_number", "issued_at"]
    
    