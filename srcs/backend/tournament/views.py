from django.http import JsonResponse
from collections import namedtuple
from .forms import TournamentForm, AliasForm
from .decorators import login_required_json
from django.contrib.auth.decorators import login_required
from .models import Tournament, Player, Match
from django.utils.functional import SimpleLazyObject
from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.

""" #TODO: to be replaced by real database
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
mockNumPlayers = 4 # num_players """


@login_required_json
def tournament(request):
    print("tournament")
    """The tournament page for BeePong."""
    if request.method != "POST":
        print("NOT POST")
        # Fetch tournaments from the database, ordered by the most recent
        tournaments = Tournament.objects.all().order_by("-tournament_id")
        form = AliasForm(username=request.user.username)
    else:
        print("POST")
        tournament_id = request.POST.get("tournament_id")
        username = request.session.get("username", None)
        form = AliasForm(data=request.POST, username=username)
        if form.is_valid():
            # Save the alias or perform other actions
            return JsonResponse(
                {"success": True, "redirect": f"/tournament/{tournament_id}/lobby"},
                status=201,
            )
        else:
            return JsonResponse({"success": False, "errors": form.errors}, status=400)

    # Prepare tournaments data for the template
    tournament_data = []
    print("num of tournaments:", tournaments.count())
    for tournament in tournaments:
        print(
            "tournament:",
            tournament.tournament_id,
        )
        players = list(tournament.players.values("username"))
        player_usernames = [player["username"] for player in players]
        winner_username = tournament.winner.username if tournament.winner else ""
        tournament_data.append(
            {
                "tournament_id": tournament.tournament_id,
                "name": tournament.title,
                "description": tournament.description,
                "state": tournament.state,
                "num_players": tournament.num_players,
                "players": player_usernames,
                "winner": winner_username,
            }
        )
    print("before render")
    print("tournament_data:", tournament_data)
    return render(
        request,
        "tournament/tournament.html",
        {
            "tournaments": tournament_data,
            "form": form,
            "form_action": "/tournament/",
        },
    )


def solo_game(request):
    return render(request, "tournament/solo_game.html")


@login_required_json
def create_tournament(request):
    """The create tournament page for BeePong."""
    if request.method != "POST":
        form = TournamentForm()
    else:
        form = TournamentForm(request.POST)
        if form.is_valid():
            tournament = form.save(commit=False)
            tournament.save()
            form.save_m2m()
            players = list(tournament.players.values("username"))
            player_usernames = [player["username"] for player in players]
            return JsonResponse(
                {
                    "success": True,
                    "redirect": "/tournament",
                    "name": tournament.title,
                    "description": tournament.description,
                    "num_players": tournament.num_players,
                    "tournament_id": tournament.tournament_id,
                    "state": tournament.state,
                    "players": player_usernames,
                    "winner": "",
                },
                status=201,
            )
        else:
            return JsonResponse({"success": False, "errors": form.errors}, status=400)
    return render(
        request,
        "tournament/create_tournament.html",
        {"form": form, "form_action": "/tournament/create/"},
    )


@login_required
def tournament_lobby(request, tournament_id):
    print("views.py tournament_lobby")
    """The tournament lobby page for BeePong."""
    if request.method == "POST":
        form = AliasForm(request.POST)
        if form.is_valid():
            # In your tournament view
            # form = AliasForm(username=request.user.username)
            print("the form is valid")
    try:
        # Safely retrieve the tournament object
        tournament = get_object_or_404(Tournament, tournament_id=tournament_id)
        players = list(tournament.players.values("username"))
        usernames = [player["username"] for player in players]
        num_players_in_tournament = tournament.players.count()
        print("num_players_in_tournament:", num_players_in_tournament)
        if tournament.state == "NEW":
            user1 = request.user
            if tournament.is_user_in_tournament(user1):
                print(f"{user1} is in the list.")
            else:
                print(f"{user1} is not in the list.")
                print(f"Adding {user1} to the list.")
                player, _ = Player.objects.get_or_create(user=request.user)

                player.is_online = True
                player.username = request.user.username
                print("created or got player", player.username)
                if player.has_active_tournament == False:
                    print(
                        "player has no active tournament, adding them to this tournament"
                    )
                    player.current_tournament_id = tournament_id
                    player.has_active_tournament = True
                    player.save()
                    tournament.players.add(player)
                else:
                    print("player already has an active tournament")
                    return JsonResponse(
                        {
                            "success": False,
                            "error": "Player already has an active tournament",
                        },
                        status=404,
                    )
                # if tournament.players.count() >= tournament.num_players:
                #     print("tournament is full, starting the tournament")
                #     tournament.state = "PLAYING"
                tournament.save()
        print("tournament_lobby ready to render")
        if (
            tournament.state == "NEW"
            and tournament.players.count() < tournament.num_players
        ):
            return render(
                request,
                "tournament/tournament_waiting_lobby.html",
                {
                    "players_in_lobby": usernames,
                    "num_players_in_tournament": num_players_in_tournament,
                    "num_players": tournament.num_players,
                },
            )
        if tournament.state == "PLAYING":
            print("tournament is playing, rendering canvas")
            return render(
                request,
                "tournament/tournament_game.html",
                {
                    "players_in_lobby": usernames,
                    "num_players_in_tournament": num_players_in_tournament,
                    "num_players": tournament.num_players,
                },
            )
        # todo: do it in a new way now that matches list is in tournament
        matches = Match.objects.filter(
            tournament=tournament
        )  # Retrieve all matches associated with the tournament
        lose_players = [
            match.determine_loser().username for match in matches
        ]  # TODO: replace username with alias
        if tournament.winner:
            return render(
                request,
                "tournament/tournament_winner.html",
                {
                    "players_in_lobby": usernames,
                    "num_players": tournament.num_players,
                    "lose_players": lose_players,
                },
            )
        else:
            return render(
                request,
                "tournament/tournament_full_lobby.html",
                {
                    "match_players": usernames,
                    "players_in_lobby": usernames,
                    "num_players": tournament.num_players,
                    "lose_players": lose_players,
                    "is_final": tournament.is_final,
                },
            )
    except Exception as error:
        print(error)
        return JsonResponse({"success": False, "error": str(error)}, status=404)


# TODO: only players in the tournament can access its lobby page
# @login_required_json
# def tournament_lobby(request, tournament_id):
#    """The tournament lobby page for BeePong."""
#    return render(request, 'tournament/tournament_lobby.html', {'match_players': mockMatchPlayers, 'players_in_lobby': mockPlayersInLobby, 'num_players': mockNumPlayers})
