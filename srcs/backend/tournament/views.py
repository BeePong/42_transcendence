from django.http import JsonResponse
from collections import namedtuple
from .forms import TournamentForm, AliasForm
from .decorators import login_required_json
from django.http import JsonResponse
from collections import namedtuple
from django.contrib.auth.decorators import login_required
from .models import Tournament, Player, Match
from .decorators import login_required_json
from django.utils.functional import SimpleLazyObject
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
# Create your views here.

@login_required_json
def tournament(request):
    """The tournament page for BeePong."""
    player, created = Player.objects.get_or_create(user=request.user)
    if request.method != 'POST':
        # Fetch tournaments from the database, ordered by the most recent
        tournaments = Tournament.objects.all().order_by('-tournament_id')
        form = AliasForm(username=request.user.username)
    else:
        tournament_id = request.POST.get('tournament_id')
        #username = request.session.get('username', None)
        form = AliasForm(data=request.POST, instance=player)
        if form.is_valid():
            if player.has_active_tournament == False:
                form.save()
         #Safely retrieve the tournament object
            tournament = get_object_or_404(Tournament, tournament_id=tournament_id)
            if tournament.state != 'READY':
                #user1 = request.user
                list_players = tournament.players
                if player.alias in list_players:
                    print(f"{player.alias} is in the list.")
                else:
                    print(f"{player.alias} is not in the list.")
                    player.is_online = True
                    if player.has_active_tournament == False:
                        player.current_tournament_id = tournament_id
                        player.has_active_tournament = True
                        player.save()
                        tournament.players.append(player.alias)
                        tournament.num_players_in += 1
                if tournament.num_players_in >= tournament.num_players:
                   tournament.state = 'READY'
                tournament.save()
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
    return render(request, 'tournament/tournament.html', {
        'tournaments': tournament_data,
        'form': form,
        'form_action': '/tournament/',
    })



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
    return render(request, 'tournament/create_tournament.html', {'form': form, 'form_action': reverse('tournament:create_tournament')})





@login_required
def tournament_lobby(request, tournament_id):
    """The tournament lobby page for BeePong.""" 
    try:
        #Safely retrieve the tournament object
        tournament = get_object_or_404(Tournament, tournament_id=tournament_id)
        if tournament.state != 'READY' and tournament.num_players_in < tournament.num_players:
            return render(request, 'tournament/tournament_waiting_lobby.html', {'players_in_lobby': tournament.players, 'num_players': tournament.num_players})
        
        matches = Match.objects.filter(tournament=tournament) # Retrieve all matches associated with the tournament
        lose_players = [match.determine_loser().alias for match in matches] #TODO: replace username with alias
        if tournament.winner:
            return render(request, 'tournament/tournament_winner.html', {'players_in_lobby': tournament.players, 'num_players': tournament.num_players, 'lose_players': lose_players})
        else:
            return render(request, 'tournament/tournament_full_lobby.html', {'match_players': tournament.players, 'players_in_lobby': tournament.players, 'num_players': tournament.num_players, 'lose_players': lose_players, 'is_final': tournament.is_final})
    except Exception as error:
        return JsonResponse({'success': False, 'error': error}, status=404)
