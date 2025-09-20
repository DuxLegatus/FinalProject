import io
from rest_framework.permissions import IsAdminUser,AllowAny,IsAuthenticated
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .models import Booking,Ticket
from .serializers import BookingSerializer,TicketSerializer
from .pagination import PaginationLimitOffset
import qrcode
from reportlab.lib.utils import ImageReader
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.http import HttpResponse

# Create your views here.

class BookingListCreateView(APIView):
    pagination_class = PaginationLimitOffset
    def get_permissions(self):
        return [IsAuthenticated()]
    def get(self,request):
        bookings = Booking.objects.all().filter(status="confirmed")
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
        serializer = TicketSerializer(page, many=True)
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
    

class TicketPDFAPIView(APIView):
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
            return Response({"detail":"not found"},status=status.HTTP_404_NOT_FOUND)
        if ticket.booking.user != request.user:
            return Response({"deatail":"forbidden"},status=status.HTTP_403_FORBIDDEN)
        
        qr = qrcode.QRCode(box_size=10, border=4)
        qr.add_data(ticket.ticket_number)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        qr_buffer = io.BytesIO()
        img.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)
        qr_image = ImageReader(qr_buffer)

        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        p.drawString(280, 800, f"Ticket")
        p.drawString(100, 700, f"Ticket Number: {ticket.ticket_number}")
        p.drawString(100, 680, f"Passenger: {ticket.booking.first_name} {ticket.booking.last_name}")
        p.drawString(100, 660, f"Train: {ticket.booking.schedule.train.name}")
        p.drawString(100, 640, f"Seat: {ticket.booking.seat.seat_number}")
        p.drawImage(qr_image, 100, 200, width=150, height=150)
        p.showPage()
        p.save()
        buffer.seek(0)

        return HttpResponse(buffer, content_type='application/pdf')
