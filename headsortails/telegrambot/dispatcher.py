import logging
import datetime

from django.conf import settings
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater
from telegram import InlineKeyboardButton
from telegrambot.jobs import every_day_job

import telegrambot.commands as commands


def setup_dispatcher(dp):
    dp.add_handler(CommandHandler('start', commands.start))
    dp.add_handler(CommandHandler('play', commands.play))
    dp.add_handler(CommandHandler('leaderboard', commands.get_leader_dashboard))
    dp.add_handler(CommandHandler('gamehistory', commands.get_game_history))
    dp.add_handler(CommandHandler('help', commands.get_help))

    # unknown handler
    dp.add_handler(MessageHandler(Filters.command, commands.unknown))
    return dp


def run_pooling():
    """Run bot in pooling mode"""
    updater = Updater(
        token=settings.TOKEN
    )
    dispatcher = updater.dispatcher
    dispatcher = setup_dispatcher(dispatcher)

    # Create job
    jobs = updater.job_queue
    every_day_job(jobs)

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    updater.start_polling()
    # updater.idle()  # Ctrl+C click handler
