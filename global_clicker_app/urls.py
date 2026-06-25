from django.contrib import admin
from django.urls import path
from global_clicker_app import views

urlpatterns = [
    path("clicker/", views.clicker, name="clicker"),
    path("", views.redirect_to_clicker, name="redirect"),
    path("clicker/click", views.click, name="click")
]