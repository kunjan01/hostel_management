from django.shortcuts import redirect
from django.urls import path

from . import views

urlpatterns = [
    path("health/", views.health_check, name="health_check"),
    path("", lambda req: redirect("dashboard"), name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),
]
