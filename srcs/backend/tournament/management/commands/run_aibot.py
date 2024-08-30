from django.core.management.base import BaseCommand
import asyncio
from ...ai import ai_bot, login


class Command(BaseCommand):
    help = "Runs the AI bot"

    def add_arguments(self, parser):
        parser.add_argument("--tournament_id", dest="tournament_id", type=int)

    async def async_handle(self, *args, **options):
        session = login()
        tournament_id = (
            options["tournament_id"] or 1
        )  # Default to tournament 1 if id not specified
        await ai_bot(session, tournament_id)

    def handle(self, *args, **options):
        # Use asyncio.ensure_future or asyncio.create_task if within an event loop
        asyncio.ensure_future(self.async_handle(*args, **options))
