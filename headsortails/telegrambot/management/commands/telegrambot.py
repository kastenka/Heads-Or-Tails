from django.core.management import BaseCommand

from telegrambot.dispatcher import run_pooling


class Command(BaseCommand):
    help = "Telegram Bot 'Heads Or Tails'"

    def handle(self, *args, **kwargs):
        run_pooling()

