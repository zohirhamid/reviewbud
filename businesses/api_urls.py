from django.urls import path
from . import api_views

urlpatterns = [
    path("businesses/", api_views.business_list, name="business_list"),
    path("businesses/create/", api_views.business_create, name="business_create"),
    path("businesses/<int:pk>/", api_views.business_detail, name="business_detail"),
    path("businesses/<int:pk>/update/", api_views.business_update, name="business_update"),
    path("businesses/<int:pk>/delete/", api_views.business_delete, name="business_delete"),
]
