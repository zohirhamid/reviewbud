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

    # Access review link details
    path('review-links/<int:id>/', api_views.ReviewLinkDetailView.as_view(), name='review_link_detail_api'),

    # Customer-facing
    path('reviews/<uuid:token>/', api_views.SubmitReviewView.as_view(), name='submit_review'),

    # Owner dashboard
    path('reviews/', api_views.ReviewListView.as_view(), name='review_list'),
]
