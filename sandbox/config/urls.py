from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from home import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_page, name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("auth/sabia/", include("django_sabia_auth.urls")),
    path("admin/", admin.site.urls),
]
