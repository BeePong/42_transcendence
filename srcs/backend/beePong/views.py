from django.shortcuts import render, redirect
from django.http import Http404
from django.http import JsonResponse
from accounts.forms import CustomAuthenticationForm
import os
from urllib.parse import urlencode
from collections import namedtuple
from .forms import TournamentForm, AliasForm
from .decorators import login_required_json

# Create your views here.

#TODO: to be replaced by real database
MockTournaments = namedtuple('MockTournaments', ['tournament_id', 'name', 'description', 'state', 'num_players', 'players', 'winner'])

mock_tournaments = [
    MockTournaments(
        tournament_id=1,
        name='BEEPONG CUP', 
        description='The mighty Pong contest for the best of the best bees!', 
        state='FINISHED', 
        num_players=4,
        players=['wchan', 'lclerc', 'vvagapov', 'djames'],
        winner='wchan'
    ),
    MockTournaments(
        tournament_id=2,
        name='BEEPONG CUP', 
        description='The mighty Pong contest for the best of the best bees!', 
        state='PLAYING', 
        num_players=4,
        players=['lclerc', 'vvagapov', 'wchan', 'djames'],
        winner=None
    ),
    MockTournaments(
        tournament_id=3,
        name='WORLD CUP', 
        description='The mighty Pong contest for the best of the bestest in the world bees!', 
        state='NEW', 
        num_players=4,
        players=['overripe_banana', 'bald_potato'],
        winner=None
    ),
    MockTournaments(
        tournament_id=4,
        name='BEEPONG CUP', 
        description='The mighty Pong contest for the best of the best bees!', 
        state='NEW',
        num_players=4,
        players=['lclerc', 'vvagapov', 'wchan'],
        winner=None
    ),
]

#TODO: to be replaced by real database
# mockPlayersInLobby = ['lclerc', 'vvagapov', 'wchan', 'djames']
# mockPlayersInMatch = ['lclerc', 'vvagapov']
# mockNumPlayers = 4
mockPlayersInLobby = ['lclerc', 'vvagapov', 'wchan']
mockPlayersInMatch = ['lclerc', 'vvagapov']
mockNumPlayers = 4
# mockPlayersInLobby = ['lclerc', 'vvagapov']
# mockPlayersInMatch = ['lclerc', 'vvagapov']
# mockNumPlayers = 2

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

@login_required_json
def tournament(request):
    """The tournament page for BeePong."""
    if request.method != 'POST':
        #TODO: to be replaced by real database
        tournaments = mock_tournaments[::-1] # Reverse the tournaments to show the new tournament at the top
        form = AliasForm(username=request.user.username)
    else:
        tournament_id = request.POST.get('tournament_id')
        username = request.session.get('username', None)
        form = AliasForm(data=request.POST, username=username)
        if form.is_valid():
            # TODO: save the alias
            return JsonResponse({'success': True, 'redirect': f'/tournament/{tournament_id}/lobby'}, status=201) #TODO: also return alias in the json respsonse
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    return render(request, 'beePong/tournament.html', {'tournaments': tournaments, 'form': form, 'form_action': '/tournament/'})

@login_required_json
def create_tournament(request):
    """The create tournament page for BeePong."""
    if request.method != 'POST':
        form = TournamentForm()
    else:
        form = TournamentForm(request.POST)
        if form.is_valid():
            # TODO: save the form 
            # TODO: delete new_tournament and mock_tournaments.append because the new tournament data will be saved in the database and fetching the tournament page again should show the new tournament
            new_tournament = MockTournaments(
                tournament_id=len(mock_tournaments) + 1,
                name=form.cleaned_data['title'],
                description=form.cleaned_data['description'],
                state='NEW',
                num_players=form.cleaned_data['num_players'],
                players=[],
                winner=None
            )
            mock_tournaments.append(new_tournament)
            return JsonResponse({'success': True, 'redirect': '/tournament'}, status=201) #TODO: also return title, description and number of players in the json respsonse
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    return render(request, 'beePong/create_tournament.html', {'form': form, 'form_action': '/tournament/create/'})

#TODO: only players in the tournament can access its lobby page
@login_required_json
def tournament_lobby(request, tournament_id):
    """The tournament lobby page for BeePong."""
    return render(request, 'beePong/tournament_lobby.html', {'players_in_match': mockPlayersInMatch, 'players_in_lobby': mockPlayersInLobby, 'num_players': mockNumPlayers})

def custom_404(request, exception):
    """The 404 page for BeePong."""
    return render(request, 'beePong/404.html', status=404)

# Needed for health check in docker-compose.yml
def health_check(request):
    return JsonResponse({"status": "healthy"})
