from django.shortcuts import render, redirect

def redirect_to_clicker(request):
    return redirect("/clicker/")

def clicker(request):
    clicks = 0 # fetch em later with like Click.objects.all() or something

    return render(request, "global_clicker_app/templates/clicker.html", {
        "clicks": clicks
    })
