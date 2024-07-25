from django.shortcuts import render, redirect
from django.http import Http404
from django.http import JsonResponse
from accounts.forms import CustomAuthenticationForm
import os
from urllib.parse import urlencode
from collections import namedtuple
from .forms import TournamentForm

# Create your views here.

MockTournaments = namedtuple('MockTournaments', ['tournament_id', 'name', 'description', 'state', 'num_players', 'players', 'winner'])

# Create some mock data
mock_tournaments = [
    MockTournaments(
        tournament_id=1,
        name='BEEPONG CUP', 
        description='The mighty Pong contest for the best of the best bees!', 
        state='NEW',
        num_players=4,
        players=['lclerc', 'vvagapov', 'wchan'],
        winner=None
    ),
    MockTournaments(
        tournament_id=2,
        name='WORLD CUP', 
        description='The mighty Pong contest for the best of the bestest in the world bees!', 
        state='NEW', 
        num_players=2,
        players=['overripe_banana', 'bald_potato'],
        winner=None
    ),
    MockTournaments(
        tournament_id=3,
        name='BEEPONG CUP', 
        description='The mighty Pong contest for the best of the best bees!', 
        state='PLAYING', 
        num_players=4,
        players=['lclerc', 'vvagapov', 'wchan', 'djames'],
        winner=None
    ),
    MockTournaments(
        tournament_id=4,
        name='BEEPONG CUP', 
        description='The mighty Pong contest for the best of the best bees!', 
        state='FINISHED', 
        num_players=4,
        players=['wchan', 'lclerc', 'vvagapov', 'djames'],
        winner='wchan'
    ),
]

def test(request):
    data = {"test": "This is a test JSON"}
    return JsonResponse(data)

def navbar(request):
    """The navbar for BeePong."""
    return render(request, 'beePong/navbar.html')

def home(request):
    """The home page for BeePong."""
    params = {
        'client_id': os.getenv('FTAPI_UID'),
        'redirect_uri': os.getenv('FTAPI_REDIR_URL'),
        'response_type': 'code',
        'scope': 'public',
        'state': 'qwerty',
    }
    login_url = f"https://api.intra.42.fr/oauth/authorize?{urlencode(params)}"
    return render(request, 'beePong/home.html', {'42_login_url': login_url})
    # return render(request, 'beePong/home.html')

def about(request):
    """The about page for BeePong."""
    return render(request, 'beePong/about.html')

def game(request):
    """The game page for BeePong."""
    return render(request, 'beePong/game.html')

def tournament(request):
    """The tournament page for BeePong."""
    tournaments = mock_tournaments
    context = {'tournaments': tournaments}
    if request.user.is_authenticated:
        return render(request, 'beePong/tournament.html', context)
    return JsonResponse({'authenticated': False}, status=401)

def create_tournament(request):
    """Handle the creation of a new tournament."""
    if request.method == 'POST':
        form = TournamentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('tournament_list')  # Replace with your tournament list view
    else:
        form = TournamentForm()
    return render(request, 'beePong/create_tournament.html', {'form': form})


def custom_404(request, exception):
    """The 404 page for BeePong."""
    return render(request, 'beePong/404.html', status=404)