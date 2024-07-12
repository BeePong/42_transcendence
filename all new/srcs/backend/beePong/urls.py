from django.urls import path
from . import views

app_name = 'beePong'
urlpatterns = [
    # Home page
    path('', views.index, name='index'),
    path('api/', views.test, name='apiTest'),
]