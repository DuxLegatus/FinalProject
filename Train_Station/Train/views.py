from django.utils import timezone
from .models import Train,TrainSchedule,Seat,Carriage
from .serializers import TrainSerializer,CarriageSerializer,SeatSerializer,TrainScheduleSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser,AllowAny
from booking.models import Booking
from .pagination import PaginationLimitOffset


class TrainListCreateAPIView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":  
            return [IsAdminUser()]
        return [AllowAny()] 

    def get(self,request):
        trains = Train.objects.all()
        serializer = TrainSerializer(trains,many = True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    def post(self,request):
        serializer = TrainSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CarriageListCreateAPIView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":  
            return [IsAdminUser()]
        return [AllowAny()] 

    def get(self,request):
        carriages = Carriage.objects.all()
        serializer = CarriageSerializer(carriages,many = True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    def post(self,request):
        serializer = CarriageSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SeatListAPIView(APIView):
    pagination_class = PaginationLimitOffset
    def get(self, request):
        schedule_id = request.query_params.get("schedule")
        available = request.query_params.get("available")
        class_type = request.query_params.get("class_type")

        seats = Seat.objects.all()

        if schedule_id:
            seats = seats.filter(carriage__train__schedules__id=schedule_id)

        if available == "true":
            booked_seats = Booking.objects.filter(
                schedule_id=schedule_id, 
                status="confirmed"
            ).values_list("seat_id", flat=True)

            seats = seats.exclude(id__in=booked_seats)

        elif available == "false":
            booked_seats = Booking.objects.filter(
                schedule_id=schedule_id, 
                status="confirmed"
            ).values_list("seat_id", flat=True)

            seats = seats.filter(id__in=booked_seats)

        if class_type in ["first", "second"]:
            seats = seats.filter(carriage__class_type=class_type)
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(seats, request, view=self)
        serializer = SeatSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
    


class TrainScheduleListCreateAPIView(APIView):
    pagination_class = PaginationLimitOffset
    def get_permissions(self):
        if self.request.method == "POST":  
            return [IsAdminUser()]
        return [AllowAny()] 

    def get(self,request):
        train_schedule = TrainSchedule.objects.filter(arrival_time__gte=timezone.now())
        starting_location = request.query_params.get("starting_location")
        final_destination = request.query_params.get("final_destination")
        departure_date = request.query_params.get("departure_date")
        if starting_location:
            train_schedule = train_schedule.filter(starting_location__iexact=starting_location)
        if final_destination:
            train_schedule = train_schedule.filter(final_destination__iexact=final_destination)
        if departure_date:
            train_schedule = train_schedule.filter(departure_date__date=departure_date)
        
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(train_schedule, request, view=self)
        serializer = TrainScheduleSerializer(page,many = True)
        return paginator.get_paginated_response(serializer.data)
    
    def post(self,request):
        serializer = TrainScheduleSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TrainScheduleRetrieveUpdateDestroyAPIView(APIView):
    def get_permissions(self):
        if self.request.method in ["PUT","PATCH","DELETE"]:
            return [IsAdminUser()]
        return [AllowAny()]
    
    
    def get_object(self,pk):
        try:
            return TrainSchedule.objects.get(pk=pk)
        except TrainSchedule.DoesNotExist:
            return None
        
    def get(self,request,pk):
        schedule = self.get_object(pk=pk)
        if not schedule:
            return Response({"detail": "Not Found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = TrainScheduleSerializer(schedule)
        return Response(serializer.data)
    
    def put(self,request,pk):
        schedule = self.get_object(pk)
        if not schedule:
            return Response({"detail": "Not Found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = TrainScheduleSerializer(schedule, data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self,request,pk):
        schedule = self.get_object(pk)
        if not schedule:
            return Response({"detail": "Not Found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = TrainScheduleSerializer(schedule, data = request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        schedule = self.get_object(pk)
        if not schedule:
            return Response({"detail": "Not Found"}, status=status.HTTP_404_NOT_FOUND)
        schedule.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
