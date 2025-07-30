"""Routes."""

from django.urls import path

from . import views

app_name = "evemap"

urlpatterns = [
    path("", views.index, name="index"),
    path(
        "solar_systems_geojson",
        views.solar_systems_geojson,
        name="solar_systems_geojson",
    ),
]
