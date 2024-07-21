from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.



def test(request):
    data = {"test": "This is a test JSON"}
    return JsonResponse(data)

def pong(request):
    return render(request, 'beePong/pong.html')

def navbar(request):
    """The navbar for BeePong."""
    return render(request, 'beePong/navbar.html')

def home(request):
    """The home page for BeePong."""
    return render(request, 'beePong/home.html')

def about(request):
    """The about page for BeePong."""
    return render(request, 'beePong/about.html')

def custom_404(request, exception):
    """The 404 page for BeePong."""
    return render(request, 'beePong/404.html', status=404)
