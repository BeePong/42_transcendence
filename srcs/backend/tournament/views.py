from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .forms import TournamentForm, AliasForm
from .models import Tournament, Player, Match
from .decorators import login_required_json

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
        form = AliasForm(data=request.POST, instance=player)
        if form.is_valid():
            if not player.has_active_tournament:
                form.save()
                
            # Safely retrieve the tournament object
            tournament = get_object_or_404(Tournament, tournament_id=tournament_id)
            if tournament.state != 'READY':
                if not tournament.players.filter(player_id=player.player_id).exists():
                    print(f"{player.alias} is not in the list. Adding to the tournament.")
                    player.is_online = True
                    player.current_tournament_id = tournament_id
                    player.has_active_tournament = True
                    player.save()
                    tournament.players.add(player)
                    tournament.save()

                    
                if tournament.players.count() >= tournament.num_players:
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
            'players': list(tournament.players.values('alias')),
            'winner': tournament.winner.alias if tournament.winner else None,
        })
    return render(request, 'tournament/tournament.html', {
        'tournaments': tournament_data,
        'form': form,
        'form_action': '/tournament/',
    })

@login_required
def solo_game(request):
    """Render the solo game page."""
    return render(request, "tournament/solo_game.html")

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
                'players': list(tournament.players.values('alias')),
                'winner': tournament.winner.alias if tournament.winner else None
            }, status=201)
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    return render(request, 'tournament/create_tournament.html', {'form': form, 'form_action': '/tournament/create/'})


@login_required
def tournament_lobby(request, tournament_id):
    """The tournament lobby page for BeePong.""" 
    try:
        # Safely retrieve the tournament object
        tournament = get_object_or_404(Tournament, tournament_id=tournament_id)
        if tournament.state != 'READY' and tournament.players.count() < tournament.num_players:
            return render(request, 'tournament/tournament_waiting_lobby.html', {
                'players_in_lobby': list(tournament.players.values('alias')),
                'num_players': tournament.num_players,
            })
        
        matches = Match.objects.filter(tournament=tournament) # Retrieve all matches associated with the tournament
        lose_players = [match.determine_loser().alias for match in matches] # TODO: replace username with alias
        
        if tournament.winner:
            return render(request, 'tournament/tournament_winner.html', {
                'players_in_lobby': list(tournament.players.values('alias')),
                'num_players': tournament.num_players,
                'lose_players': lose_players,
            })
        else:
            return render(request, 'tournament/tournament_full_lobby.html', {
                'match_players': list(tournament.players.values('alias')),
                'players_in_lobby': list(tournament.players.values('alias')),
                'num_players': tournament.num_players,
                'lose_players': lose_players,
                'is_final': tournament.is_final,
            })
    except Exception as error:
        return JsonResponse({'success': False, 'error': str(error)}, status=404)
