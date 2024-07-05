from django.urls import path
from . import views

app_name = 'beePong'
urlpatterns = [
    path('api/', views.test, name='apiTest'),
    path('home/', views.home, name='home'),
    path('about/', views.about, name='about'),
]