from django.urls import path
from . import apiviews

app_name = 'businesses_api'

urlpatterns = [
    # List all businesses (dashboard equivalent)
    path('businesses/', apiviews.DashboardView.as_view(), name='dashboard_api'),

    # Create a new business
    path('businesses/create/', apiviews.CreateBusinessView.as_view(), name='create_business_api'),

    # Retrieve a single business
    path('businesses/<int:id>/', apiviews.BusinessDetailView.as_view(), name='business_detail_api'),

    # Access review link details
    path('review-links/<int:id>/', apiviews.ReviewLinkDetailView.as_view(), name='review_link_detail_api'),

    # Customer-facing
    path('reviews/<uuid:token>/', apiviews.SubmitReviewView.as_view(), name='submit_review'),

    # Owner dashboard
    path('reviews/', apiviews.ReviewListView.as_view(), name='review_list'),
]
