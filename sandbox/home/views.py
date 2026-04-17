from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def index(request):
    return render(request, "home/index.html")


def login_page(request):
    context = {}
    if settings.DEBUG:
        context["sabia_client_id"] = getattr(settings, "SABIA_CLIENT_ID", "")
        context["sabia_redirect_uri"] = getattr(settings, "SABIA_REDIRECT_URI", "")
    return render(request, "home/login.html", context)


@login_required
def dashboard(request):
    return render(request, "home/dashboard.html")
