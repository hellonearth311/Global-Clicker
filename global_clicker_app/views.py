from django.shortcuts import render

def clicker(request):
    return render(request, "global_clicker_app/templates/clicker.html")
