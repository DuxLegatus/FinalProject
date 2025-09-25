from django.utils import timezone
from decimal import Decimal
from django.db import models
from Train.models import Train, Seat
from django.contrib.auth.models import User
import uuid

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    schedule = models.ForeignKey("Train.TrainSchedule", on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    personal_number = models.CharField(max_length=20)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    booking_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[("confirmed", "Confirmed"), ("cancelled", "Cancelled")],
        default="confirmed"
    )
    class Meta:
        unique_together = ('schedule', 'seat','personal_number')
    def save(self, *args, **kwargs):
        if not self.price: 
            base_price = self.schedule.price
            class_type = self.seat.carriage.class_type
            if class_type == "first":

                self.price = base_price * Decimal("1.50")
            else:
                self.price = base_price
        super().save(*args, **kwargs)

    def __str__(self):
         return f"Booking by {self.user} for {self.seat.carriage.train} seat {self.seat.seat_number} on {self.schedule.departure_time}"
    

class Ticket(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    train_schedule = models.ForeignKey("Train.TrainSchedule", on_delete=models.CASCADE, editable=False)
    ticket_number = models.CharField(max_length=20, unique=True,editable=False)
    issued_at = models.DateTimeField(auto_now_add=True)


    def save(self, *args, **kwargs):
        if not self.ticket_number:
            self.ticket_number = str(uuid.uuid4().hex[:16]).upper()
        super().save(*args, **kwargs)
    def is_outdated(self):
        return self.train_schedule.arrival_time < timezone.now()
    

    def __str__(self):
        return f"Ticket {self.ticket_number} for {self.booking.user}"