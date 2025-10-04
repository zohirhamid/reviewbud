from django.urls import path
from . import api_views

app_name = 'businesses_api'

urlpatterns = [
    # List all businesses (dashboard equivalent)
    path('businesses/', api_views.DashboardView.as_view(), name='dashboard_api'),

    # Create a new business
    path('businesses/create/', api_views.CreateBusinessView.as_view(), name='create_business_api'),

    # Retrieve a single business
    path('businesses/<int:id>/', api_views.BusinessDetailView.as_view(), name='business_detail_api'),

    # Update or delete a business
    path('businesses/<int:id>/update/', api_views.UpdateBusinessView.as_view(), name='update_business_api'),
]
