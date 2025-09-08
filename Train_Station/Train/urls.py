from django.urls import path,include
from .views import TrainListCreateAPIView,TrainScheduleListCreateAPIView,SeatListAPIView,CarriageListCreateAPIView,TrainScheduleRetrieveUpdateDestroyAPIView

urlpatterns = [
    path("trains/",TrainListCreateAPIView.as_view(),name="trains"),
    path("train-schedules/",TrainScheduleListCreateAPIView.as_view(),name="train-schedules"),
    path("train-schedule/<int:pk>",TrainScheduleRetrieveUpdateDestroyAPIView.as_view(),name="train-schedule"),
    path("carriages/",CarriageListCreateAPIView.as_view(), name = "carriages"),
    path("seats/",SeatListAPIView.as_view(),name="seats")
]