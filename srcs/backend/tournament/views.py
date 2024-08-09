from django.http import JsonResponse
from collections import namedtuple
from .forms import TournamentForm, AliasForm
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Tournament, Player
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
    return render(request, 'tournament/tournament.html', {'tournaments': tournaments, 'form': form, 'form_action': '/tournament/'})

@login_required_json
def create_tournament(request):
    """The create tournament page for BeePong."""
    if request.method != 'POST':
        form = TournamentForm()
    else:
        form = TournamentForm(request.POST)
        if form.is_valid():
            print("the form is valid")
            tournament = form.save(commit=False)
            tournament.save()  # Save the tournament instance first
            if not tournament.players:
                tournament.players = []
            # Now you can add players to the many-to-many field
            form.save_m2m()
            # Convert the players to a list of player IDs or names
            players_list = list(tournament.players.values_list('id', flat=True))
            return JsonResponse({
                'success': True,
                'redirect': '/tournament',
                'name': tournament.title,
                'description': tournament.description,
                'num_players': tournament.num_players,
                'tournament_id': tournament.tournament_id,
                'state': tournament.state,
                'players': players_list,
                'winner': tournament.winner
            }, status=201)
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    return render(request, 'tournament/create_tournament.html', {'form': form, 'form_action': '/tournament/create/'})
#TODO: only players in the tournament can access its lobby page
@login_required_json
def tournament_lobby(request, tournament_id):
    """The tournament lobby page for BeePong."""
    return render(request, 'tournament/tournament_lobby.html')