# quickrate/urls.py
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect


def root_redirect(request):
    return redirect('businesses:landing_page')

urlpatterns = [
    path('', root_redirect),
    path('admin/', admin.site.urls),
    path('', include('businesses.urls')),
    path('reviews/', include('reviews.urls')),
]