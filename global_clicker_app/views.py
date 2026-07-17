import time

from django.core.cache import cache
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from ipware import get_client_ip
from .models import Click, PendingClick
CLICK_RATE_LIMIT = 10
CLICK_RATE_WINDOW = 1 

def get_user_ip(request):
    client_ip, is_routable = get_client_ip(request, proxy_order="right-most")
    if client_ip:
        return client_ip

def is_rate_limited(ip_address):
    if not ip_address:
        return False
    bucket = int(time.time()) // CLICK_RATE_WINDOW
    key = f"click-rate:{ip_address}:{bucket}"
    count = cache.get(key, 0) + 1
    cache.set(key, count, timeout=CLICK_RATE_WINDOW + 1)
    return count > CLICK_RATE_LIMIT

def redirect_to_clicker(request):
    return redirect("/clicker/")

def clicker(request):
    clicks = Click.objects.all()
    pendingClicks = PendingClick.objects.all()

    totalClicks = clicks.count() + pendingClicks.count()

    display_clicks = [
        {
            "lat": float(click.latitude),
            "lng": float(click.longitude),
        }
        for click in clicks
        if click.latitude is not None and click.longitude is not None
    ]

    top_countries = [
        {"name": row["country"], "clicks": row["clicks"]}
        for row in clicks.exclude(country__isnull=True)
        .values("country")
        .annotate(clicks=Count("id"))
        .order_by("-clicks")[:10]
    ]

    return render(request, "global_clicker_app/templates/clicker.html", {
        "clicks": totalClicks,
        "clicks_list": display_clicks,
        "countries": top_countries
    })

@require_POST
def click(request):
    ip_address = get_user_ip(request)

    if is_rate_limited(ip_address):
        total = Click.objects.count() + PendingClick.objects.count()
        return JsonResponse(
            {"clicks": total, "error": "rate_limited"}, status=429
        )

    PendingClick.objects.create(ip_address=ip_address)

    total = Click.objects.count() + PendingClick.objects.count()
    return JsonResponse({"clicks": total})