from django.urls import path
from . import views

app_name = 'beePong'
urlpatterns = [
    path('api/', views.test, name='apiTest'),
    path('navbar/', views.navbar, name='navbar'),
    path('home/', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('custom_404_frontend/', views.custom_404_frontend, name='custom_404_frontend'),
    path('health/', views.health_check, name='health_check'),
]
