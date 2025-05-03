from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'), 
    path('logout/', views.logout_view, name='logout'),
    path("register/", views.register, name="register"),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path("orders/", views.user_orders, name="user_orders"),
     path('sales/', views.sales_report_view, name='sales'),  # Define 'sales' here

    path('admin/sales/download/', views.download_sales_csv, name='download_sales_csv'),
]
