import logging
import datetime

from django.conf import settings
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

from telegrambot.commands import (
    start,
    play,
    get_leader_dashboard,
    get_game_history,
    unknown,
    get_help
)
from telegrambot.jobs import every_day_job


def setup_dispatcher(dp):
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('play', play))
    dp.add_handler(CommandHandler('leaderboard', get_leader_dashboard))
    dp.add_handler(CommandHandler('gamehistory', get_game_history))
    dp.add_handler(CommandHandler('help', get_help))

    # unknown handler
    dp.add_handler(MessageHandler(Filters.command, unknown))
    return dp


def run_pooling():
    """ Run bot in pooling mode """
    updater = Updater(
        token=settings.TOKEN
    )
    dispatcher = updater.dispatcher
    dispatcher = setup_dispatcher(dispatcher)

    # create job
    jobs = updater.job_queue
    every_day_job(jobs)

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    updater.start_polling()
    # updater.start_polling(timeout=123)
    # updater.idle()
