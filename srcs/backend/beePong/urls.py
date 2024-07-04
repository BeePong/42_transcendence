from django.urls import path
from . import views

app_name = 'beePong'
urlpatterns = [
    path('api/', views.test, name='apiTest'),
    path('page/home/', views.home, name='home'),
    path('page/about/', views.about, name='about'),
]