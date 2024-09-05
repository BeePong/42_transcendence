from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from .forms import TournamentForm, AliasForm
from .decorators import login_required_json
from .models import Tournament, Player, Match
import logging

logger = logging.getLogger(__name__)


@login_required_json
def tournament(request):
    logger.info("Tournament view called")
    player, _ = Player.objects.get_or_create(user=request.user)

    if request.method == "POST":
        return handle_tournament_post(request, player)

    tournaments = Tournament.objects.all().order_by("-tournament_id")
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
            "form_action": "/tournament/",
        },
    )


def handle_tournament_post(request, player):
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
        handle_new_tournament(tournament, player, form)
    else:
        logger.info(
            f"Tournament {tournament_id} is not in NEW state. Current state: {tournament.state}"
        )

    tournament.refresh_from_db()
    logger.info(f"Tournament {tournament_id} final state: {tournament.state}")

    return JsonResponse(
        {
            "success": True,
            "redirect": f"/tournament/{tournament_id}/lobby",
            "tournament_state": tournament.state,
        },
        status=201,
    )


def handle_new_tournament(tournament, player, form):
    logger.info(
        f"Adding player {player.username} to tournament {tournament.tournament_id}"
    )
    form.save()

    if player not in tournament.players.all():
        tournament.players.add(player)
        player.has_active_tournament = True
        player.current_tournament_id = tournament.tournament_id
        player.save()
        tournament.save()
        logger.info(
            f"Player {player.username} added to tournament {tournament.tournament_id}"
        )

    if tournament.is_full():
        logger.info(
            f"Tournament {tournament.tournament_id} has enough players. Starting tournament."
        )
        tournament.state = "PLAYING"
        tournament.save()
    else:
        logger.info(
            f"Tournament {tournament.tournament_id} doesn't have enough players yet. Current: {tournament.players.count()}, Required: {tournament.num_players}"
        )


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
    logger.info("Tournament lobby view called")
    try:
        tournament = get_object_or_404(Tournament, tournament_id=tournament_id)
        context = prepare_tournament_context(tournament)
        logger.info(f"Context: {context}")

        if tournament.state == "NEW" and not tournament.is_full():
            return render_waiting_lobby(request, context)

        if tournament.state == "PLAYING":
            return render_game_canvas(request, context)

        if tournament.winner:
            return render_winner_page(request, context)

        return render_full_lobby(request, context)

    except Exception as error:
        logger.error(f"Error in tournament lobby: {error}", exc_info=True)
        return JsonResponse({"success": False, "error": str(error)}, status=404)


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
    context.update(
        {
            "match_players": context["players_in_lobby"],
            "is_final": context["num_players"] == 2,
        }
    )
    return render(request, "tournament/tournament_full_lobby.html", context)
