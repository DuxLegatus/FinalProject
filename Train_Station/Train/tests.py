from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from datetime import timedelta
from .models import Train, TrainSchedule, Carriage, Seat

class BaseAPITestCase(APITestCase):
    def setUp(self):
        Train.objects.all().delete()
        TrainSchedule.objects.all().delete()
        Carriage.objects.all().delete()
        Seat.objects.all().delete()
        self.admin_user = User.objects.create_user(username="admin", password="adminpass", is_staff=True)
        refresh = RefreshToken.for_user(self.admin_user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

class TrainAPITests(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.train_url = reverse("trains")
        self.train = Train.objects.create(name="Express", status="active")

    def test_list_trains(self):
        response = self.client.get(self.train_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Express")

    def test_create_train(self):
        data = {"name": "Regional", "status": "active"}
        response = self.client.post(self.train_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Train.objects.count(), 2)

class CarriageAPITests(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.train = Train.objects.create(name="Express", status="active")
        self.carriage_url = reverse("carriages")

    def test_list_carriages(self):
        Carriage.objects.create(train=self.train, carriage_number=1, seats=10, class_type="first")
        response = self.client.get(self.carriage_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_carriage_and_seats(self):
        data = {"train": self.train.id, "carriage_number": 2, "seats": 3, "class_type": "first"}
        response = self.client.post(self.carriage_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Carriage.objects.count(), 1)
        self.assertEqual(Seat.objects.count(), 3)

class SeatAPITests(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.train = Train.objects.create(name="Regional", status="active")
        self.carriage = Carriage.objects.create(train=self.train, carriage_number=1, seats=3, class_type="first")
        for i in range(3):
            Seat.objects.create(carriage=self.carriage, seat_number=i + 1)
        self.seats_url = reverse("seats")

    def test_list_seats(self):
        response = self.client.get(self.seats_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 3)

class TrainScheduleAPITests(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.train = Train.objects.create(name="Express", status="active")
        self.schedule_url = reverse("train-schedules")
        self.now = timezone.now()
        self.future_departure = self.now + timedelta(days=1)
        self.future_arrival = self.future_departure + timedelta(hours=2)

    def test_list_train_schedules_empty(self):
        response = self.client.get(self.schedule_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)

    def test_create_train_schedule(self):
        data = {"train_id": self.train.id, "starting_location": "City A", "final_destination": "City B",
                "departure_date": self.future_departure.isoformat(), "arrival_time": self.future_arrival.isoformat(),
                "status": "on_time", "price": "50.00"}
        response = self.client.post(self.schedule_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TrainSchedule.objects.count(), 1)

    def test_retrieve_train_schedule(self):
        schedule = TrainSchedule.objects.create(train=self.train, starting_location="City A", final_destination="City B",
                                                departure_date=self.future_departure, arrival_time=self.future_arrival,
                                                status="on_time", price=30)
        url = reverse("train-schedule", args=[schedule.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["starting_location"], "City A")

    def test_update_train_schedule(self):
        schedule = TrainSchedule.objects.create(train=self.train, starting_location="City A", final_destination="City B",
                                                departure_date=self.future_departure, arrival_time=self.future_arrival,
                                                status="on_time", price=30)
        url = reverse("train-schedule", args=[schedule.id])
        response = self.client.patch(url, {"status": "delayed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        schedule.refresh_from_db()
        self.assertEqual(schedule.status, "delayed")

    def test_delete_train_schedule(self):
        schedule = TrainSchedule.objects.create(train=self.train, starting_location="City A", final_destination="City B",
                                                departure_date=self.future_departure, arrival_time=self.future_arrival,
                                                status="on_time", price=30)
        url = reverse("train-schedule", args=[schedule.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(TrainSchedule.objects.count(), 0)
