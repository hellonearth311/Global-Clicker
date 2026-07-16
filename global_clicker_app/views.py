from django.shortcuts import render, redirect
from ipware import get_client_ip
from .models import Click, PendingClick

def get_user_ip(request):
    client_ip, is_routable = get_client_ip(request, proxy_count=1)
    if client_ip:
        return client_ip

def redirect_to_clicker(request):
    return redirect("/clicker/")

def clicker(request):
    clicks = Click.objects.all().count() + PendingClick.objects.all().count()

    return render(request, "global_clicker_app/templates/clicker.html", {
        "clicks": clicks
    })

def click(request):
    ip_address = get_user_ip(request)

    PendingClick.objects.create(ip_address=ip_address)
    return redirect('/clicker/')