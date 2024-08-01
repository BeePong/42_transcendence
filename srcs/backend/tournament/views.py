from django.shortcuts import render
from django.http import JsonResponse
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
mockPlayersInLobby = ['lclerc', 'vvagapov'] # players waiting in the lobby, including the current user who clicks the join button
mockMatchPlayers = ['lclerc', 'vvagapov'] # current user and the opponent, if the lobby is full. None otherwise.
mockNumPlayers = 4 # num_players

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
    return render(request, 'tournament/create_tournament.html', {'form': form, 'form_action': '/tournament/create/'})

#TODO: only players in the tournament can access its lobby page
@login_required_json
def tournament_lobby(request, tournament_id):
    """The tournament lobby page for BeePong."""
    return render(request, 'tournament/tournament_lobby.html', {'match_players': mockMatchPlayers, 'players_in_lobby': mockPlayersInLobby, 'num_players': mockNumPlayers})