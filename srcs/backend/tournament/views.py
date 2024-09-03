from django.http import JsonResponse
from collections import namedtuple
from .forms import TournamentForm, AliasForm
from .decorators import login_required_json
from django.http import JsonResponse
from collections import namedtuple
from django.contrib.auth.decorators import login_required
from .models import Tournament, Player, Match
from django.utils.functional import SimpleLazyObject
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
import asyncio
import logging
from asgiref.sync import async_to_sync

# Create your views here.


@login_required_json
def tournament(request):
    logging.info("Tournament view called")
    """The tournament page for BeePong."""
    player, created = Player.objects.get_or_create(user=request.user)
    if request.method != "POST":
        print("NOT POST")
        # Fetch tournaments from the database, ordered by the most recent
        tournaments = Tournament.objects.all().order_by("-tournament_id")
        form = AliasForm(username=request.user.username)
    else:
        print("POST")
        tournament_id = request.POST.get("tournament_id")
        # username = request.session.get('username', None)
        form = AliasForm(data=request.POST, instance=player)
        if form.is_valid():
            print("form is valid")
            tournament = get_object_or_404(Tournament, tournament_id=tournament_id)
            logging.info(
                f"Tournament state: {tournament.state}, Players: {tournament.players.count()}/{tournament.num_players}"
            )

            if tournament.state == "NEW":
                logging.info(
                    f"Adding player {player.username} to tournament {tournament_id}"
                )
                form.save()

                if player not in tournament.players.all():
                    tournament.players.add(player)
                    player.has_active_tournament = True
                    player.current_tournament_id = tournament.tournament_id
                    player.save()
                    tournament.save()
                    logging.info(
                        f"Player {player.username} added to tournament {tournament_id}"
                    )

                # Check if the tournament should start
                if tournament.players.count() == tournament.num_players:
                    logging.info(
                        f"Tournament {tournament_id} has enough players. Attempting to start."
                    )
                    tournament.state = "PLAYING"
                    tournament.save()
                    async_to_sync(tournament.start_tournament_if_applicable)()
                else:
                    logging.info(
                        f"Tournament {tournament_id} doesn't have enough players yet. Current: {tournament.players.count()}, Required: {tournament.num_players}"
                    )
            else:
                logging.info(
                    f"Tournament {tournament_id} is not in NEW state. Current state: {tournament.state}"
                )

            tournament.refresh_from_db()  # Refresh the tournament object to get the latest state
            logging.info(f"Tournament {tournament_id} final state: {tournament.state}")

            return JsonResponse(
                {
                    "success": True,
                    "redirect": f"/tournament/{tournament_id}/lobby",
                    "tournament_state": tournament.state,
                },
                status=201,
            )
        else:
            logging.warning(f"Form is invalid: {form.errors}")
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
        {"form": form, "form_action": reverse("tournament:create_tournament")},
    )


@login_required
def tournament_lobby(request, tournament_id):
    print("views.py tournament_lobby")
    """The tournament lobby page for BeePong."""
    try:
        # Safely retrieve the tournament object
        tournament = get_object_or_404(Tournament, tournament_id=tournament_id)

        players = list(tournament.players.values("username"))
        usernames = [player["username"] for player in players]
        num_players_in_tournament = tournament.players.count()
        print("num_players_in_tournament:", num_players_in_tournament)
        # if tournament.state == "NEW":
        #     user1 = request.user
        #     if tournament.is_user_in_tournament(user1):
        #         print(f"{user1} is in the list.")
        #     else:
        #         print(f"{user1} is not in the list.")
        #         print(f"Adding {user1} to the list.")
        #         player, _ = Player.objects.get_or_create(user=request.user)

        #         player.is_online = True
        #         player.username = request.user.username
        #         print("created or got player", player.username)
        #         if player.has_active_tournament == False:
        #             print(
        #                 "player has no active tournament, adding them to this tournament"
        #             )
        #             player.current_tournament_id = tournament_id
        #             player.has_active_tournament = True
        #             player.save()
        #             tournament.players.add(player)
        #         else:
        #             print("player already has an active tournament")
        #             return JsonResponse(
        #                 {
        #                     "success": False,
        #                     "error": "Player already has an active tournament",
        #                 },
        #                 status=404,
        #             )
        #         # if tournament.players.count() >= tournament.num_players:
        #         #     print("tournament is full, starting the tournament")
        #         #     tournament.state = "PLAYING"
        #         tournament.save()
        print("tournament_lobby ready to render")
        print("num_players_in_tournament before rendering:", num_players_in_tournament)
        if (
            tournament.state == "NEW"
            and num_players_in_tournament < tournament.num_players
        ):
            print("tournament is new, rendering waiting lobby")
            return render(
                request,
                "tournament/tournament_waiting_lobby.html",
                {
                    "players_in_lobby": usernames,
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
            match.determine_loser().alias for match in matches
        ]  # TODO: replace username with alias

        if tournament.winner:
            print("tournament has a winner, rendering winner page")
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
            print("tournament is not new, playing, or finished, rendering full lobby")
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
