"""Views."""

from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse
from django.shortcuts import render
from eveuniverse.models import EveSolarSystem


@login_required
@permission_required("evemap.basic_access")
def index(request):
    """Render index view."""

    context = {"text": "Hello, World!"}
    return render(request, "evemap/index.html", context)


@login_required
@permission_required("evemap.basic_access")
def solar_systems_geojson(request):
    features = []
    for system in EveSolarSystem.objects.all():
        features.append(
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [system.position_x, system.position_z],
                },
                "properties": {
                    "id": system.id,
                    "name": system.name,
                    "security_status": system.security_status,
                },
            }
        )
    geojson = {"type": "FeatureCollection", "features": features}
    return JsonResponse(geojson)
