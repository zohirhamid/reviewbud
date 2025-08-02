from django.urls import path
from . import views

app_name = 'businesses'

urlpatterns = [
    path('home/', views.landing_page, name='landing_page'),

    # Authentication
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard (login required)
    path('dashboard/', views.dashboard, name='dashboard'),
    path('create/', views.create_business, name='create_business'),

    # qr code
    path('qr_code/<uuid:token>/', views.qr_code, name='qr_code'),
    path('create-qrcode/<str:token>/', views.create_qr_code_page, name='create_qr_code')
]