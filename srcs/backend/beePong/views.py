from django.shortcuts import render, redirect
from django.http import Http404
from django.http import JsonResponse
from accounts.forms import CustomAuthenticationForm

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

def game(request):
    """The game page for BeePong."""
    return render(request, 'beePong/game.html')

def tournament(request):
    """The tournament page for BeePong."""
    if request.user.is_authenticated:
        return render(request, 'beePong/tournament.html')
    return JsonResponse({'authenticated': False}, status=401)

def custom_404(request, exception):
    """The 404 page for BeePong."""
    return render(request, 'beePong/404.html', status=404)