from django.shortcuts import render
from django.http import JsonResponse
from collections import namedtuple
from .forms import TournamentForm, AliasForm
from .decorators import login_required_json
from django.http import JsonResponse
from collections import namedtuple
from .forms import TournamentForm, AliasForm
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Tournament, Player
from .decorators import login_required_json
from django.utils.functional import SimpleLazyObject
from .forms import AliasForm
from django.shortcuts import render, redirect, get_object_or_404
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
        # Fetch tournaments from the database, ordered by the most recent
        tournaments = Tournament.objects.all().order_by('-tournament_id')
        form = AliasForm(username=request.user.username)
    else:
        tournament_id = request.POST.get('tournament_id')
        username = request.session.get('username', None)
        form = AliasForm(data=request.POST, username=username)
        if form.is_valid():
            # Save the alias or perform other actions
            return JsonResponse({'success': True, 'redirect': f'/tournament/{tournament_id}/lobby'}, status=201)
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    
    # Prepare tournaments data for the template
    tournament_data = []
    for tournament in tournaments:
        tournament_data.append({
            'tournament_id': tournament.tournament_id,
            'name': tournament.title,
            'description': tournament.description,
            'state': tournament.state,
            'num_players': tournament.num_players,
            'players': tournament.players,
            'winner': tournament.winner,
        })
    print(tournament_data)
    return render(request, 'tournament/tournament.html', {
        'tournaments': tournament_data,
        'form': form,
        'form_action': '/tournament/',
    })
#@login_required_json
#def tournament(request):
#    """The tournament page for BeePong."""
#    if request.method != 'POST':
#        #TODO: to be replaced by real database
#        tournaments = mock_tournaments[::-1] # Reverse the tournaments to show the new tournament at the top
#        form = AliasForm(username=request.user.username)
#    else:
#        tournament_id = request.POST.get('tournament_id')
#        username = request.session.get('username', None)
#        form = AliasForm(data=request.POST, username=username)
#        if form.is_valid():
#            # TODO: save the alias
#            return JsonResponse({'success': True, 'redirect': f'/tournament/{tournament_id}/lobby'}, status=201) #TODO: also return alias in the json respsonse
#        else:
#            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
#    return render(request, 'tournament/tournament.html', {'tournaments': tournaments, 'form': form, 'form_action': '/tournament/'})



@login_required_json
def create_tournament(request):
    """The create tournament page for BeePong."""
    if request.method != 'POST':
        form = TournamentForm()
    else:
        form = TournamentForm(request.POST)
        if form.is_valid():
            tournament = form.save(commit=False)
            tournament.save()
            form.save_m2m()
            return JsonResponse({
                'success': True,
                'redirect': '/tournament',
                'name': tournament.title,
                'description': tournament.description,
                'num_players': tournament.num_players,
                'tournament_id': tournament.tournament_id,
                'state': tournament.state,
                'players': tournament.players,
                'winner': tournament.winner
            }, status=201)
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    return render(request, 'tournament/create_tournament.html', {'form': form, 'form_action': '/tournament/create/'})
#@login_required_json
#def create_tournament(request):
#    """The create tournament page for BeePong."""
#    if request.method != 'POST':
#        form = TournamentForm()
#    else:
#        form = TournamentForm(request.POST)
#        if form.is_valid():
#            # TODO: save the form 
#            # TODO: delete new_tournament and mock_tournaments.append because the new tournament data will be saved in the database and fetching the tournament page again should show the new tournament
#            new_tournament = MockTournaments(
#                tournament_id=len(mock_tournaments) + 1,
#                name=form.cleaned_data['title'],
#                description=form.cleaned_data['description'],
#                state='NEW',
#                num_players=form.cleaned_data['num_players'],
#                players=[],
#                winner=None
#            )
#            mock_tournaments.append(new_tournament)
#            return JsonResponse({'success': True, 'redirect': '/tournament'}, status=201) #TODO: also return title, description and number of players in the json respsonse
#        else:
#            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
#    return render(request, 'tournament/create_tournament.html', {'form': form, 'form_action': '/tournament/create/'})
#



@login_required
def tournament_lobby(request, tournament_id):
    """The tournament lobby page for BeePong."""
    print("hola vamos a ver si funciona")
    #if request.method == 'POST':
    #   form = PlayerForm(request.POST)
    #   if form.is_valid():
    #       player, _ = Player.objects.get_or_create(user=request.user)
    #       player.alias = form.cleaned_data['alias']
    #       player.save()
    #       print(f"The form is valid, player alias saved: {player.alias}")
    #   else:
    #       print("The form is not valid")
    if request.method == 'POST':
        form = AliasForm(request.POST)
        if form.is_valid():
            # In your tournament view
            #form = AliasForm(username=request.user.username)

            print("the form is valid")
            #player = form.save(commit=False)
            #player.user = request.user  # Link the player to the current user
            #player.save()
            #
    print("estoy en loby")
    try:
        # Safely retrieve the tournament object
        tournament = get_object_or_404(Tournament, tournament_id=tournament_id)
        if tournament.state != 'READY':
            user1 = request.user
            list_players = tournament.players
            if user1.username in list_players:
                print(f"{user1} is in the list.")
            else:
               print(f"{user1} is not in the list.")
               player, _ = Player.objects.get_or_create(user=request.user)
               player.is_online = True
               player.username = request.user.username
               if player.is_registered == False:
                   player.current_tournament_id = tournament_id
                   player.is_registered = True
                   player.save()
                   tournament.players.append(player.username)
                   tournament.num_players_in += 1
               if tournament.num_players_in >= tournament.num_players:
                   tournament.state = 'READY'
               tournament.save()
        return render(request, 'tournament/tournament_lobby.html', {'match_players': tournament.players, 'players_in_lobby': tournament.players, 'num_players': tournament.num_players})
        #return render(request, 'tournament/tournament_lobby.html')
    except Exception as error:
        return JsonResponse({'success': False, 'error': error}, status=404)
##TODO: only players in the tournament can access its lobby page
#@login_required_json
#def tournament_lobby(request, tournament_id):
#    """The tournament lobby page for BeePong."""
#    return render(request, 'tournament/tournament_lobby.html', {'match_players': mockMatchPlayers, 'players_in_lobby': mockPlayersInLobby, 'num_players': mockNumPlayers})