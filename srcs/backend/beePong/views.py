
from django.shortcuts import render, redirect
from django.http import Http404
from django.http import JsonResponse
from accounts.forms import CustomAuthenticationForm
from collections import namedtuple

# Create your views here.

def test(request):
    data = {"test": "This is a test JSON"}
    return JsonResponse(data)

def navbar(request):
    """The navbar for BeePong."""
    return render(request, 'beePong/navbar.html')

def home(request):
    """The home page for BeePong."""
    return render(request, 'beePong/home.html')

def about(request):
    """The about page for BeePong."""
    return render(request, 'beePong/about.html')

""" def solo_game(request):
    return render(request, 'tournament/solo_game.html') """

def game(request):
    """The game page for BeePong."""
    return render(request, 'beePong/game.html')

def custom_404(request, exception):
    """The 404 page for BeePong."""
    return render(request, 'beePong/error.html', {'error_message': '404 not found'}, status=404)

# Needed for health check in docker-compose.yml
def health_check(request):
    return JsonResponse({"status": "healthy"})
