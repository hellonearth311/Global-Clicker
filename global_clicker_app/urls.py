from django.contrib import admin
from django.urls import path
from global_clicker_app import views

urlpatterns = [
    path("clicker/", views.clicker, name="clicker")
]