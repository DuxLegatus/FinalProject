from django.db import models
from django.utils import timezone 
# Create your models here.


class Train(models.Model):
    name = models.CharField(max_length=20,unique=True)
    status = models.CharField(max_length=50,choices=[("active", "Active"), ("maintenance", "Maintenance")], default="active")

    def __str__(self):
        return f"train:{self.name}, status:{self.status}"
    
class TrainSchedule(models.Model):
    train = models.ForeignKey(Train, on_delete=models.CASCADE, related_name="schedules")
    starting_location = models.CharField(max_length=100)
    final_destination = models.CharField(max_length=100)
    departure_date = models.DateTimeField()
    arrival_time = models.DateTimeField()
    status = models.CharField(max_length=50,choices=[("on_time","On Time"),("delayed","Delayed"),("cancelled","Cancelled"),("outdated","Outdated")],default="on_time")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=20)

    def __str__(self):
        return f"{self.train} on {self.departure_date} from {self.starting_location} to {self.final_destination}"
    def is_outdated(self): 
        return self.arrival_time < timezone.now()


class Carriage(models.Model):
    train = models.ForeignKey(Train, on_delete=models.CASCADE)
    carriage_number = models.IntegerField()
    seats = models.IntegerField()
    class_type = models.CharField(max_length=20, choices=[("first", "First Class"), ("second", "Second Class")])
    def __str__(self):
        return f"carriage number: {self.carriage_number}"


class Seat(models.Model):
    carriage = models.ForeignKey(Carriage,on_delete=models.CASCADE)
    seat_number = models.IntegerField()
    def __str__(self):
        return f"seat number: {self.seat_number}"
    
