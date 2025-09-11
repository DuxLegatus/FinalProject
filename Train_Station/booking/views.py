from rest_framework.permissions import IsAdminUser,AllowAny,IsAuthenticated
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .models import Booking,Ticket
from .serializers import BookingSerializer,TicketSerializer
from .pagination import PaginationLimitOffset
# Create your views here.

class BookingListCreateView(APIView):
    pagination_class = PaginationLimitOffset
    def get_permissions(self):
        return [IsAuthenticated()]
    def get(self,request):
        bookings = Booking.objects.all().filter(user=request.user,status="confirmed")
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(bookings, request, view=self)
        serializer = BookingSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    def post(self,request):
        serializer = BookingSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class BookingRetrieveDestroy(APIView):
    def get_permissions(self):
        return [IsAuthenticated()]
    
    def get_object(self,pk):
        try:
            return Booking.objects.get(pk=pk)
        except Booking.DoesNotExist:
            return None
    
    def get(self,request,pk):
        booking = self.get_object(pk)
        if not booking:
            return Response({"detail": "Not Found"}, status=status.HTTP_404_NOT_FOUND)
        if booking.user != request.user:
            return Response({"detail": "Not Allowed"}, status=status.HTTP_403_FORBIDDEN)
        serializer = BookingSerializer(booking)
        return Response(serializer.data)
    
    def delete(self, request, pk):
        booking = self.get_object(pk)
        if not booking:
            return Response({"detail": "Not Found"}, status=status.HTTP_404_NOT_FOUND)
        if booking.user != request.user:
            return Response({"detail": "Not Allowed"}, status=status.HTTP_403_FORBIDDEN)
        booking.status = "cancelled"
        booking.save()
        
        return Response({"detail": "Booking cancelled successfully"}, status=status.HTTP_200_OK)
    

class TicketListAPIView(APIView):
    pagination_class = PaginationLimitOffset
    def get_permissions(self):
        return [IsAuthenticated()]

    def get(self, request):
        tickets = Ticket.objects.filter(booking__user=request.user)
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(tickets, request, view=self)
        serializer = BookingSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
class TicketRetrieveAPIView(APIView):
    def get_permissions(self):
        return [IsAuthenticated()]
    def get_object(self,pk):
        try:
            return Ticket.objects.get(pk=pk)
        except Ticket.DoesNotExist:
            return None
    
    def get(self,request,pk):
        ticket = self.get_object(pk)
        if not ticket:
            return Response({"detail" : "Not Found"},status=status.HTTP_404_NOT_FOUND)
        if ticket.booking.user != request.user:
            return Response({"detail": "Not Allowed"}, status=status.HTTP_403_FORBIDDEN)
        serializer = TicketSerializer(ticket)
        return Response(serializer.data)
    def delete(self, request, pk):
        ticket = self.get_object(pk)
        if not ticket:
            return Response({"detail": "Not Found"}, status=status.HTTP_404_NOT_FOUND)
        if ticket.booking.user != request.user:
            return Response({"detail": "Not Allowed"}, status=status.HTTP_403_FORBIDDEN)
        
        ticket.booking.status = "cancelled"
        ticket.booking.save()
        
        return Response({"detail": "Ticket cancelled successfully"}, status=status.HTTP_200_OK)