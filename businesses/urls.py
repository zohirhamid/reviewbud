from django.urls import path
from . import views

app_name = 'businesses'

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('create/', views.create_business, name='create_business'),
    path('business/<int:id>/', views.business_detail, name='business_detail'),
    path('edit/<int:id>/', views.update_business, name='update_business'),
    path('delete/<int:id>/', views.delete_business, name='delete_business'),
    
    # Authentication
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # QR code
    path('qr_code/<uuid:token>/', views.qr_code, name='qr_code'),
    path('create-qrcode/<str:token>/', views.create_qr_code_page, name='create_qr_code'),

    # settings
    path('settings/', views.settings_view, name='settings'),

    # Stripe Checkout URLs
    #path('checkout/<str:plan>/', views.checkout_view, name='checkout'),
    #path('checkout/success/', views.checkout_success, name='checkout_success'),
    #path('checkout/cancel/', views.checkout_cancel, name='checkout_cancel'),
]
