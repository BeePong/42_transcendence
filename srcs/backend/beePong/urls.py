from django.urls import path
from . import views

app_name = 'beePong'
urlpatterns = [
    path('api/', views.test, name='apiTest'),
<<<<<<< HEAD
    path('pong/', views.pong, name='pong'),
]
=======
    path('navbar/', views.navbar, name='navbar'),
    path('home/', views.home, name='home'),
    path('about/', views.about, name='about'),
]
>>>>>>> main
