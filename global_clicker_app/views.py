from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from ipware import get_client_ip
from .models import Click, PendingClick

def get_user_ip(request):
    client_ip, is_routable = get_client_ip(request, proxy_order="right-most")
    if client_ip:
        return client_ip

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

    PendingClick.objects.create(ip_address=ip_address)

    total = Click.objects.count() + PendingClick.objects.count()
    return JsonResponse({"clicks": total})