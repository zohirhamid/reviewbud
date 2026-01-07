from django.urls import path
from .views import ReviewFormView, SubmitReviewView

app_name = 'reviews'

urlpatterns = [
    path('review/<str:token>/', ReviewFormView.as_view(), name='review_form'),
    path('review/<str:token>/submit/', SubmitReviewView.as_view(), name='submit_review'),
]