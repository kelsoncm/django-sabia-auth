from django.urls import include, path

urlpatterns = [path("auth/sabia/", include("django_sabia_auth.urls"))]
