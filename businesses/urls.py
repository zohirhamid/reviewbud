from django.urls import path
from . import views

app_name = 'businesses'

urlpatterns = [
    # FBV routes (old)
    path('', views.landing_page, name='landing_page'),

    path('dashboard/', views.dashboard, name='dashboard'),
    path('analytics/', views.analytics, name='analytics'),
    path('support/', views.support_view, name='support'),

    path('create/', views.create_business, name='create_business'),
    path('business/<int:id>/', views.business_detail, name='business_detail'),
    path('delete/<int:id>/', views.delete_business, name='delete_business'),

    path('settings/', views.settings_view, name='settings'),
    
    ## QR code
    path('qr_code/<uuid:token>/', views.qr_code, name='qr_code'),
    path('create-qrcode/<str:token>/', views.create_qr_code_page, name='create_qr_code'),
]
