from django.urls import path

from .views import SabiaCallbackView, SabiaLoginView

app_name = "sabia_auth"

urlpatterns = [
    path("login/", SabiaLoginView.as_view(), name="login"),
    path("callback/", SabiaCallbackView.as_view(), name="callback"),
]
