import secrets
import time
from collections import Counter

from django.core import signing
from django.core.cache import cache
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from ipware import get_client_ip
from .models import Click, PendingClick
CLICK_RATE_LIMIT = 15
CLICK_RATE_WINDOW = 1
LOCATION_PRECISION = 3

CLICK_TOKEN_SALT = "clicker.click-token"
CLICK_TOKEN_MAX_AGE = 600


BAN_STRIKES = 30
BAN_WINDOW = 60
BAN_SECONDS = 600

def get_user_ip(request):
    client_ip, is_routable = get_client_ip(request, proxy_order="right-most")
    if client_ip:
        return client_ip

def issue_click_token():
    return signing.TimestampSigner(salt=CLICK_TOKEN_SALT).sign(
        secrets.token_urlsafe(16)
    )

def consume_click_token(token):
    if not token:
        return False
    try:
        value = signing.TimestampSigner(salt=CLICK_TOKEN_SALT).unsign(
            token, max_age=CLICK_TOKEN_MAX_AGE
        )
    except signing.BadSignature:
        return False
    
    return cache.add(f"click-token-used:{value}", 1, timeout=CLICK_TOKEN_MAX_AGE)

def is_rate_limited(ip_address):
    if not ip_address:
        return False
    bucket = int(time.time()) // CLICK_RATE_WINDOW
    key = f"click-rate:{ip_address}:{bucket}"
    count = cache.get(key, 0) + 1
    cache.set(key, count, timeout=CLICK_RATE_WINDOW + 1)
    return count > CLICK_RATE_LIMIT

def is_banned(ip_address):
    return bool(ip_address) and cache.get(f"click-ban:{ip_address}") is not None

def record_strike(ip_address):
    if not ip_address:
        return
    key = f"click-strikes:{ip_address}"
    strikes = cache.get(key, 0) + 1
    cache.set(key, strikes, timeout=BAN_WINDOW)
    if strikes >= BAN_STRIKES:
        cache.set(f"click-ban:{ip_address}", 1, timeout=BAN_SECONDS)

def redirect_to_clicker(request):
    return redirect("/clicker/")

def clicker(request):
    clicks = Click.objects.all()
    pendingClicks = PendingClick.objects.all()

    totalClicks = clicks.count() + pendingClicks.count()

    cell_counts = Counter(
        (round(click.latitude, LOCATION_PRECISION), round(click.longitude, LOCATION_PRECISION))
        for click in clicks
        if click.latitude is not None and click.longitude is not None
    )

    display_clicks = [
        {"lat": lat, "lng": lng, "count": count}
        for (lat, lng), count in cell_counts.items()
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
        "countries": top_countries,
        "click_token": issue_click_token(),
    })

@require_POST
def click(request):
    ip_address = get_user_ip(request)

    if is_banned(ip_address):
        return JsonResponse({"error": "banned"}, status=429)

    if not consume_click_token(request.headers.get("X-Click-Token")):
        return JsonResponse({"error": "invalid_token"}, status=403)

    if is_rate_limited(ip_address):
        record_strike(ip_address)
        total = Click.objects.count() + PendingClick.objects.count()
        return JsonResponse(
            {"clicks": total, "error": "rate_limited", "token": issue_click_token()},
            status=429,
        )

    PendingClick.objects.create(ip_address=ip_address)

    total = Click.objects.count() + PendingClick.objects.count()
    return JsonResponse({"clicks": total, "token": issue_click_token()})