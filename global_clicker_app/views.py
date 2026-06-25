from django.shortcuts import render, redirect
from ipware import get_client_ip
from .models import Click

import requests

def get_user_ip(request):
    client_ip, is_routable = get_client_ip(request, proxy_count=1)
    if client_ip:
        return client_ip

def get_location_from_ip(ip_address):
    response = requests.get(f"https://ip-api.com/json/{ip_address}")
    try:
        data = response.json()
        return data.get('lat'), data.get('lon')
    except:
        return 0.0, 0.0

def redirect_to_clicker(request):
    return redirect("/clicker/")

def clicker(request):
    clicks = Click.objects.all().count()

    return render(request, "global_clicker_app/templates/clicker.html", {
        "clicks": clicks
    })

def click(request):
    ip_address = get_user_ip(request)
    lat, lon = get_location_from_ip(ip_address)

    Click.objects.create(
        ip_address = ip_address,
        latitude = lat,
        longitude = lon,
    )
    return redirect('/clicker/')