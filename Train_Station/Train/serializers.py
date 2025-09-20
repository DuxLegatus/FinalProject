from rest_framework import serializers
from .models import Train, TrainSchedule, Carriage, Seat


class CarriageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carriage
        fields = ["id","train","carriage_number","seats","class_type"]
        read_only_fields = ['id']

    def create(self, validated_data):
        carriage = super().create(validated_data)
        seats_count = carriage.seats
        Seat.objects.bulk_create([
            Seat(carriage=carriage, seat_number=i+1) for i in range(seats_count)
        ])

        return carriage
    
class SeatSerializer(serializers.ModelSerializer):
    class_type = serializers.CharField(source='carriage.class_type', read_only=True)
    
    class Meta:
        model = Seat
        fields = ["id",'carriage',"seat_number","class_type",]
        read_only_fields = ['id']


class TrainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Train
        fields = ["id","name","status"]
        read_only_fields = ['id']

class TrainScheduleSerializer(serializers.ModelSerializer):
    train = TrainSerializer(read_only=True)
    train_id = serializers.PrimaryKeyRelatedField(
        queryset=Train.objects.all(),
        write_only=True,
        source="train"
    )
    class Meta:
        model = TrainSchedule
        fields = ["id","train","starting_location","train_id","final_destination","departure_date","arrival_time","status","price"]
        read_only_fields = ["id"]
        

    