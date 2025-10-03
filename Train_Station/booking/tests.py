from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from datetime import timedelta
from Train.models import Train, TrainSchedule, Carriage, Seat
from .models import Booking, Ticket

class BaseBookingAPITestCase(APITestCase):
    def setUp(self):
        Train.objects.all().delete()
        TrainSchedule.objects.all().delete()
        Carriage.objects.all().delete()
        Seat.objects.all().delete()
        Booking.objects.all().delete()
        Ticket.objects.all().delete()
        self.user = User.objects.create_user(username="user1", password="pass")
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        self.train = Train.objects.create(name="Express", status="active")
        self.carriage = Carriage.objects.create(train=self.train, carriage_number=1, seats=3, class_type="first")
        self.seats = [Seat.objects.create(carriage=self.carriage, seat_number=i+1) for i in range(3)]
        now = timezone.now()
        self.schedule = TrainSchedule.objects.create(
            train=self.train,
            starting_location="City A",
            final_destination="City B",
            departure_date=now + timedelta(days=1),
            arrival_time=now + timedelta(days=1, hours=2),
            status="on_time",
            price=50
        )

class BookingAPITests(BaseBookingAPITestCase):
    def setUp(self):
        super().setUp()
        self.booking_url = reverse("bookings")

    def test_create_booking(self):
        data = {
            "schedule_id": self.schedule.id,
            "first_name": "John",
            "last_name": "Doe",
            "personal_number": "123456",
            "email": "john@example.com",
            "phone": "123456789",
            "seat_id": self.seats[0].id
        }
        response = self.client.post(self.booking_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Booking.objects.count(), 1)
        self.assertEqual(Ticket.objects.count(), 1)

    def test_list_bookings(self):
        booking = Booking.objects.create(
            user=self.user,
            schedule=self.schedule,
            first_name="John",
            last_name="Doe",
            personal_number="123456",
            email="john@example.com",
            phone="123456789",
            seat=self.seats[0]
        )
        response = self.client.get(self.booking_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_retrieve_booking(self):
        booking = Booking.objects.create(
            user=self.user,
            schedule=self.schedule,
            first_name="John",
            last_name="Doe",
            personal_number="123456",
            email="john@example.com",
            phone="123456789",
            seat=self.seats[0]
        )
        url = reverse("booking", args=[booking.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "John")

    def test_delete_booking(self):
        booking = Booking.objects.create(
            user=self.user,
            schedule=self.schedule,
            first_name="John",
            last_name="Doe",
            personal_number="123456",
            email="john@example.com",
            phone="123456789",
            seat=self.seats[0]
        )
        url = reverse("booking", args=[booking.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        booking.refresh_from_db()
        self.assertEqual(booking.status, "cancelled")

class TicketAPITests(BaseBookingAPITestCase):
    def setUp(self):
        super().setUp()
        self.ticket_url = reverse("tickets")
        self.booking = Booking.objects.create(
            user=self.user,
            schedule=self.schedule,
            first_name="John",
            last_name="Doe",
            personal_number="123456",
            email="john@example.com",
            phone="123456789",
            seat=self.seats[0]
        )
        self.ticket = Ticket.objects.create(
            booking=self.booking,
            train_schedule=self.schedule
        )

    def test_list_tickets(self):
        response = self.client.get(self.ticket_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_retrieve_ticket(self):
        url = reverse("ticket", args=[self.ticket.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["ticket_number"], self.ticket.ticket_number)

    def test_delete_ticket_cancels_booking(self):
        url = reverse("ticket", args=[self.ticket.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, "cancelled")

    def test_ticket_pdf_endpoint(self):
        url = reverse("ticket-pdf", args=[self.ticket.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "application/pdf")
