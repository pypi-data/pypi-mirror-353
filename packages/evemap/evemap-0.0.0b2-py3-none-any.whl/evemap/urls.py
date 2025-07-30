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
    path(
        "get_region_boundaries_geojson",
        views.get_region_boundaries_geojson,
        name="get_region_boundaries_geojson",
    ),
]
