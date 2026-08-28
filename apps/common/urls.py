from django.urls import path

from .views import live_health_check

urlpatterns = [
    path("health/live/", live_health_check, name="health-live"),
]

