from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from ipware import get_client_ip
from .models import Click, PendingClick

def get_user_ip(request):
    client_ip, is_routable = get_client_ip(request, proxy_count=1)
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

    return render(request, "global_clicker_app/templates/clicker.html", {
        "clicks": totalClicks, 
        "clicks_list": display_clicks
    })

@require_POST
def click(request):
    ip_address = get_user_ip(request)

    PendingClick.objects.create(ip_address=ip_address)

    total = Click.objects.count() + PendingClick.objects.count()
    return JsonResponse({"clicks": total})