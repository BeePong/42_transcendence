from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return HttpResponse("Hello, this is the home page.")

def register(request):
    return HttpResponse("This is the registration page.")

