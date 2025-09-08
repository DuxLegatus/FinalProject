from .models import Train,TrainSchedule,Seat,Carriage
from .serializers import TrainSerializer,CarriageSerializer,SeatSerializer,TrainScheduleSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser,AllowAny


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
    def get(self, request):
        seats = Seat.objects.all()
        serializer = SeatSerializer(seats, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    


class TrainScheduleListCreateAPIView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":  
            return [IsAdminUser()]
        return [AllowAny()] 

    def get(self,request):
        train_schedule = TrainSchedule.objects.all()
        serializer = TrainScheduleSerializer(train_schedule,many = True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
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
