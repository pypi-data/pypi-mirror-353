"""Views."""

from shapely import MultiPoint
from shapely.geometry import mapping

from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse
from django.shortcuts import render
from eveuniverse.models import EveRegion, EveSolarSystem


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
                    "constellation_id": system.eve_constellation.id,
                    "constellation_name": system.eve_constellation.name,
                    "region_id": system.eve_constellation.eve_region.id,
                    "region_name": system.eve_constellation.eve_region.name,
                },
            }
        )
    geojson = {"type": "FeatureCollection", "features": features}
    return JsonResponse(geojson)


@login_required
@permission_required("evemap.basic_access")
def get_region_boundaries_geojson(request):
    regions = {}
    for system in EveSolarSystem.objects.all():
        regions.setdefault(system.eve_constellation.eve_region.id, []).append(system)

    features = []
    for region_id, systems in regions.items():
        points = [[system.position_x, system.position_z] for system in systems]
        if len(points) < 3:
            continue
        multipoint = MultiPoint(points)
        hull = multipoint.convex_hull
        region_name = EveRegion.objects.get(id=region_id).name
        features.append(
            {
                "type": "Feature",
                "geometry": mapping(hull),
                "properties": {
                    "region_id": region_id,
                    "region_name": region_name,
                },
            }
        )

    geojson = {"type": "FeatureCollection", "features": features}
    return JsonResponse(geojson)
