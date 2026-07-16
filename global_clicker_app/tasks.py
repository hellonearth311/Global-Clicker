import requests
from background_task import background
from django.db import transaction

from .models import Click, PendingClick

FLUSH_INTERVAL_SECONDS = 30
BATCH_LIMIT = 100


def _lookup_locations(ip_addresses):
    ips = [ip for ip in ip_addresses if ip]
    if not ips:
        return {}

    try:
        response = requests.post(
            "http://ip-api.com/batch",
            json=[{"query": ip} for ip in ips],
            timeout=10,
        )
        results = response.json()
    except (requests.RequestException, ValueError):
        return {}

    locations = {}
    for ip, result in zip(ips, results):
        if isinstance(result, dict) and result.get("status") == "success":
            locations[ip] = (result.get("lat"), result.get("lon"))
    return locations


@background(schedule=FLUSH_INTERVAL_SECONDS)
def flush_pending_clicks():
    pending = list(PendingClick.objects.order_by("id")[:BATCH_LIMIT])
    if not pending:
        return

    locations = _lookup_locations({p.ip_address for p in pending})

    clicks = [
        Click(
            ip_address=p.ip_address,
            latitude=locations.get(p.ip_address, (0.0, 0.0))[0],
            longitude=locations.get(p.ip_address, (0.0, 0.0))[1],
            timestamp=p.timestamp,
        )
        for p in pending
    ]

    with transaction.atomic():
        Click.objects.bulk_create(clicks)
        PendingClick.objects.filter(id__in=[p.id for p in pending]).delete()
