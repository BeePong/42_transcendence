from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Tournament, Player

@receiver(post_save, sender=Tournament)
def update_player_tournament_status(sender, instance, **kwargs):
    if instance.is_final:
        players = instance.players.all()
        for player in players:
            player.current_tournament_id = -1
            player.has_active_tournament = False
            player.save()