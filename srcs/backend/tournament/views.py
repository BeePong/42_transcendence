import logging

from asgiref.sync import async_to_sync
from beePong.views import custom_404
from channels.layers import get_channel_layer
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.contrib.auth import get_user_model

from .decorators import login_required_json
from .forms import AliasForm, TournamentForm
from .models import Match, Player, Tournament
import subprocess
import os
from django.conf import settings

logger = logging.getLogger(__name__)


@login_required_json
def tournament(request):
    logger.info("Tournament view called")
    player, _ = Player.objects.get_or_create(user=request.user)

    if request.method == "POST":
        return handle_tournament_join_request(request, player)

    # Filter out tournaments with the title "Solo Tournament"
    tournaments = Tournament.objects.exclude(title="Solo Tournament").order_by(
        "-tournament_id"
    )
    form = AliasForm(user=request.user)
    tournament_data = prepare_tournament_data(tournaments, player)

    logger.debug(f"Number of tournaments: {len(tournament_data)}")
    logger.debug(f"Tournament data: {tournament_data}")

    return render(
        request,
        "tournament/tournament.html",
        {
            "tournaments": tournament_data,
            "form": form,
            "form_action": reverse("tournament:tournament"),
        },
    )


def handle_tournament_join_request(request, player):
    try:
        tournament_id = request.POST.get("tournament_id")
        form = AliasForm(data=request.POST, instance=player, user=request.user)

        if not form.is_valid():
            logger.warning(f"Form is invalid: {form.errors}")
            return JsonResponse({"success": False, "errors": form.errors}, status=400)

        tournament = get_object_or_404(Tournament, tournament_id=tournament_id)
        logger.info(
            f"Tournament state: {tournament.state}, Players: {tournament.players.count()}/{tournament.num_players}"
        )

        if tournament.state == "NEW":
            join_waiting_lobby(tournament, player, form)
        else:
            logger.info(
                f"Tournament {tournament_id} is not in NEW state. Current state: {tournament.state}"
            )

        tournament.refresh_from_db()
        logger.info(f"Tournament {tournament_id} final state: {tournament.state}")

        return JsonResponse(
            {
                "success": True,
                "redirect": f"/tournament/{tournament_id}/lobby/",
                "tournament_state": tournament.state,
            },
            status=201,
        )
    except Exception as error:
        logger.error(f"Error in tournament post: {error}", exc_info=True)
        return JsonResponse({"success": False, "error": str(error)}, status=400)


def send_message_to_all(tournament_id, message, message_type):
    pong_group_name = f"group_{tournament_id}"
    logger.info(
        f"Sending {message_type} message to all from views.py in group {pong_group_name}"
    )
    channel_layer = get_channel_layer()
    try:
        async_to_sync(channel_layer.group_send)(
            pong_group_name,
            {
                "type": "send_message",
                "message": message,
                "message_type": message_type,
            },
        )
    except Exception as e:
        print(f"Error sending message to all: {e}")


def form_new_player_message(tournament, player):
    return {
        "event": "new_player",
        "player_alias": player.alias,
        "num_players_in_tournament": tournament.players.count(),
        "num_players": tournament.num_players,
        "player1_alias": "Player1_alias",
        "player2_alias": "Player2_alias",
    }


def form_game_started_message():
    return {
        "event": "game_started",
    }


def form_countdown_message(player1_alias, player2_alias, countdown):
    return {
        "event": "countdown",
        "countdown": countdown,
        # "player1_alias": player1_alias,
        # "player2_alias": player2_alias,
    }


def join_waiting_lobby(tournament, player, form):
    logger.info(
        f"Adding player {player.username} with alias {player.alias} to tournament {tournament.tournament_id}"
    )
    form.save()

    if player.has_active_tournament:
        return JsonResponse(
            {"success": False, "error": "Player already has an active tournament"},
            status=400,
        )

    if player not in tournament.players.all():
        add_player_to_tournament(player, tournament)
        message = form_new_player_message(tournament, player)
        send_message_to_all(tournament.tournament_id, message, "tournament")

    if tournament.is_full():
        start_tournament(tournament)
    else:
        logger.info(
            f"Tournament {tournament.tournament_id} doesn't have enough players yet. Current: {tournament.players.count()}, Required: {tournament.num_players}"
        )


def add_player_to_tournament(player, tournament):
    tournament.players.add(player)
    player.has_active_tournament = True
    player.current_tournament_id = tournament.tournament_id
    player.save()
    tournament.save()
    logger.info(
        f"Player {player.username} with alias {player.alias} added to tournament {tournament.tournament_id}"
    )


def start_tournament(tournament):
    logger.info(
        f"Tournament {tournament.tournament_id} has enough players. Starting tournament."
    )
    logger.info(
        "Tournament is full, we could start countdown but fuck it MVP only so PLAYING"
    )
    # game_started_message = form_game_started_message()
    # send_message_to_all(tournament.tournament_id, game_started_message, "tournament")
    tournament.state = "PLAYING"
    tournament.is_started = False
    tournament.save()


def prepare_tournament_data(tournaments, player):
    tournament_data = []

    for tournament in tournaments:
        players = list(tournament.players.values_list("alias", flat=True))

        tournament_data.append(
            {
                "tournament_id": tournament.tournament_id,
                "name": tournament.title,
                "description": tournament.description,
                "state": tournament.state,
                "num_players": tournament.num_players,
                "players": players,
                "winner": tournament.winner.alias if tournament.winner else "",
                "has_joined": player.alias in players,
            }
        )

    return tournament_data


@login_required_json
def create_solo_game(request):
    if request.method == "POST":
        # if request.user.is_authenticated:
        tournament = Tournament.objects.create(
            title="Solo Tournament",
            num_players=2,
            description="A tournament with only one player and a dummy player.",
            state="NEW",
        )
        player, _ = Player.objects.get_or_create(user=request.user)
        tournament.players.add(player)
        player.alias = player.username
        player.has_active_tournament = True
        player.current_tournament_id = tournament.tournament_id
        player.save()
        tournament.save()

        try:
            logger.info(f"Starting AI bot for tournament {tournament.tournament_id}")
            spawn_ai_bot(tournament.tournament_id, player.alias)
        except Exception as e:
            logger.error(
                f"Error starting AI bot for tournament {tournament.tournament_id}: {e}"
            )
        if tournament.state == "NEW" and tournament.is_full():
            tournament.state = "PLAYING"
            tournament.save()
        logger.info(
            f"create solo game {tournament.tournament_id} final state: {tournament.state}"
        )

        return JsonResponse(
            {
                "success": True,
                "redirect": f"/tournament/{tournament.tournament_id}/solo_game/",
            },
            status=201,
        )
    return JsonResponse(
        {"success": False, "errors": {"non_field_errors": ["Invalid request method"]}},
        status=405,
    )


def spawn_ai_bot(tournament_id, player_alias):
    ai_script_path = os.path.join(settings.BASE_DIR, "tournament", "ai.py")
    logger.info(f"AI script path: {ai_script_path}")
    subprocess.Popen(["python", ai_script_path, str(tournament_id), player_alias])


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
            # when tournament is created, there's actually no players yet, so we can just send an empty list
            players = list(tournament.players.values("alias"))
            player_aliases = [player["alias"] for player in players]
            return JsonResponse(
                {
                    "success": True,
                    "redirect": reverse("tournament:tournament"),
                    "name": tournament.title,
                    "description": tournament.description,
                    "num_players": tournament.num_players,
                    "tournament_id": tournament.tournament_id,
                    "state": tournament.state,
                    "players": player_aliases,
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


@login_required_json
def tournament_lobby(request, tournament_id):
    logger.info("Tournament lobby view called")
    try:
        tournament = get_object_or_404(Tournament, tournament_id=tournament_id)
        context = prepare_tournament_context(tournament)
        logger.info(f"Context: {context}")
        logger.info(f"tournament.is_countdown: {tournament.is_countdown}")

        if tournament.state == "NEW" and not tournament.is_full():
            return render_waiting_lobby(request, context)

        if tournament.winner:
            context["redirect_text"], context["redirect_url"] = (
                get_winner_page_redirect_info(tournament)
            )
            return render_winner_page(request, context)

        if tournament.is_countdown:
            return render_full_lobby(request, context)

        if tournament.state == "PLAYING":
            return render_game_canvas(request, context)

        return render_full_lobby(request, context)

    except Exception as error:
        logger.error(f"Error in tournament lobby: {error}", exc_info=True)
        return custom_404(request, None)


def prepare_tournament_context(tournament):
    players = list(tournament.players.values_list("alias", flat=True))
    num_players_in_tournament = len(players)

    context = {
        "players_in_lobby": players,
        "num_players": tournament.num_players,
        "num_players_in_tournament": num_players_in_tournament,
    }

    matches = Match.objects.filter(tournament=tournament)

    # get aliases for all losers that exist. determine_loser returns either a player or none.
    lose_players = [
        match.determine_loser().alias for match in matches if match.determine_loser()
    ]
    context["lose_players"] = lose_players

    return context


def get_winner_page_redirect_info(tournament):
    if tournament.title == "Solo Tournament":
        return "BACK TO HOMEPAGE", "/"
    else:
        return "BACK TO TOURNAMENTS", reverse("tournament:tournament")


def render_waiting_lobby(request, context):
    logger.info("Rendering waiting lobby")
    return render(request, "tournament/tournament_waiting_lobby.html", context)


def render_game_canvas(request, context):
    logger.info("Rendering game canvas")
    return render(request, "tournament/tournament_game.html", context)


def render_winner_page(request, context):
    logger.info("Rendering winner page")
    return render(request, "tournament/tournament_winner.html", context)


def render_full_lobby(request, context):
    logger.info("Rendering full lobby")
    # context.update({"match_players": context["players_in_lobby"]})
    return render(request, "tournament/tournament_full_lobby.html", context)
