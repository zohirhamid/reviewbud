from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('review/<uuid:token>', views.review_form, name='review_form'),
    path('submit/<uuid:token>/', views.submit_review, name='submit_review'),
]