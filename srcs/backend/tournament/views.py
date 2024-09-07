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
    form = AliasForm(username=request.user.username)
    tournament_data = prepare_tournament_data(tournaments)

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


# TODO: the whole logic of this function, which is triggered when user click 'Join' button of a tournamet
# has to be refactored. Not working atm. It seems to always trigger the /tournament/{tournament_id}/lobby/ page
# First check if tournament_id is valid, then check that player don't have an active tournament, check if tournament is not full, and state = NEW, only then load the lobby page where webSocket connection will be triggered
def handle_tournament_join_request(request, player):
    try:
        tournament_id = request.POST.get("tournament_id")
        form = AliasForm(data=request.POST, instance=player)

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
    }


def form_game_started_message():
    return {
        "event": "game_started",
    }


def form_countdown_message(player1_alias, player2_alias, countdown):
    return {
        "event": "countdown",
        "countdown": countdown,
        "player1_alias": player1_alias,
        "player2_alias": player2_alias,
    }


def join_waiting_lobby(tournament, player, form):
    logger.info(
        f"Adding player {player.username} with alias {player.alias} to tournament {tournament.tournament_id}"
    )
    form.save()

    # Commented out for debugging purposes
    # if player.has_active_tournament:
    #   return JsonResponse(
    #      {"success": False, "error": "Player already has an active tournament"},
    #     status=400,
    # )

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


def prepare_tournament_data(tournaments):
    return [
        {
            "tournament_id": tournament.tournament_id,
            "name": tournament.title,
            "description": tournament.description,
            "state": tournament.state,
            "num_players": tournament.num_players,
            "players": [player.username for player in tournament.players.all()],
            "winner": tournament.winner.username if tournament.winner else "",
        }
        for tournament in tournaments
    ]


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
            spawn_ai_bot(tournament.tournament_id)
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

        # Create or get a dummy user for the dummy player
        # User = get_user_model()
        # dummy_user, _ = User.objects.get_or_create(
        #     username=f"dummy_user_{tournament.tournament_id}"
        # )

        # # Create or get the dummy player and associate it with the dummy user
        # dummy_player, _ = Player.objects.get_or_create(user=dummy_user)
        # dummy_player.alias = f"dummy-{tournament.tournament_id}"
        # dummy_player.has_active_tournament = True
        # dummy_player.current_tournament_id = tournament.tournament_id
        # dummy_player.save()

        # # Add the dummy player to the tournament
        # tournament.players.add(dummy_player)
        # tournament.save()

        return JsonResponse(
            {
                "success": True,
                "redirect": f"/tournament/{tournament.tournament_id}/solo_game/",
            },
            status=201,
        )
        # else:
        #     return JsonResponse({
        #         'success': False,
        #         'errors': {
        #             'non_field_errors': ['User not authenticated']
        #         }
        #     }, status=401)
    return JsonResponse(
        {"success": False, "errors": {"non_field_errors": ["Invalid request method"]}},
        status=405,
    )


def spawn_ai_bot(tournament_id):
    ai_script_path = os.path.join(settings.BASE_DIR, "tournament", "ai.py")
    logger.info(f"AI script path: {ai_script_path}")
    subprocess.Popen(["python", ai_script_path, str(tournament_id)])


@login_required_json
def solo_game(request, tournament_id):
    try:
        tournament = get_object_or_404(Tournament, tournament_id=tournament_id)
        player = Player.objects.filter(
            user=request.user, current_tournament_id=tournament.tournament_id
        ).first()
        if player:
            if tournament.winner:
                context = prepare_tournament_context(tournament)
                return render_winner_page(request, context)
            else:
                return render(
                    request, "tournament/solo_game.html", {"tournament": tournament}
                )
        else:
            return custom_404(request, None)

    except Exception as error:
        logger.error(f"Error in solo game: {error}", exc_info=True)
        return custom_404(request, None)


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


@login_required
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
    players = list(tournament.players.values_list("username", flat=True))
    num_players_in_tournament = len(players)

    context = {
        "players_in_lobby": players,
        "num_players": tournament.num_players,
        "num_players_in_tournament": num_players_in_tournament,
    }

    matches = Match.objects.filter(tournament=tournament)
    lose_players = [match.determine_loser().alias for match in matches]
    context["lose_players"] = lose_players

    return context


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
    context.update({"match_players": context["players_in_lobby"]})
    return render(request, "tournament/tournament_full_lobby.html", context)
