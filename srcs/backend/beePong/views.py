from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.


def index(request):
    """The home page for BeePong."""
    return render(request, 'beePong/index.html')

def test(request):
    data = {"test": "This is a test JSON"}
    return JsonResponse(data)

def pong(request):
    return render(request, 'beePong/pong.html')