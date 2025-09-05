from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.views.generic import CreateView
from django.urls import reverse_lazy



class RegisterUser(CreateView):
    model = User
    form_class = UserCreationForm
    template_name = "users/register.html"
    success_url = reverse_lazy("Profile")