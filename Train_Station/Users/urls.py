from django.urls import path,include
from .views import RegisterView,LoginView,LogoutView,ContactView

urlpatterns = [
    path("register/", RegisterView.as_view(),name="register"),
    path("login/", LoginView.as_view(),name="login"),
    path("logout/",LogoutView.as_view(),name="logout"),
    path("contact/", ContactView.as_view(), name="contact"),
]