from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path("users/", include("users.urls")),
    path('', include('businesses.urls')),
    path('reviews/', include('reviews.urls')),

    path("accounts/", include("allauth.urls")),
]