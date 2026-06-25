from django.shortcuts import render, redirect
from ipware import get_client_ip

def get_user_ip(request):
    client_ip, is_routable = get_client_ip(request)
    if client_ip:
        return client_ip

def redirect_to_clicker(request):
    return redirect("/clicker/")

def clicker(request):
    clicks = 0 # fetch em later with like Click.objects.all() or something
    ip = get_user_ip(request)

    return render(request, "global_clicker_app/templates/clicker.html", {
        "clicks": clicks,
        "ip": ip
    })
