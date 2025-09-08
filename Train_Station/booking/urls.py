from django.urls import path,include
from .views import *

urlpatterns = [
    path("bookings/", BookingListCreateView.as_view(),name="bookings"),
    path("booking/<int:pk>/",BookingRetrieveDestroy.as_view(),name="booking"),
    path("tickets/",TicketListAPIView.as_view(),name="tickets"),
    path("ticket/<int:pk>",TicketRetrieveAPIView.as_view(),name="ticket")
]