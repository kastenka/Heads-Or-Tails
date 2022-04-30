from telegram.ext import Updater, CallbackContext, CommandHandler, MessageHandler, Filters
from telegram import Update

from django.conf import settings
from django.contrib.sites import requests
from django.core.management import BaseCommand
from requests.exceptions import ConnectionError
import logging

import random

from aiogram import Bot, Dispatcher, executor
from telegrambot.models import Profile, Coins

from telegrambot.management.static_text_en import WRONG_INPUT_EN, HEADS, TAILS, WON, LOST


class Command(BaseCommand):
    help = "Telegram Bot 'Heads Or Tails'"

    def handle(self, *args, **kwargs):
        updater = Updater(
            token=settings.TOKEN
        )
        dispatcher = updater.dispatcher

        start_handler = CommandHandler('start', start)
        play_handler = CommandHandler('play', play)

        dispatcher.add_handler(start_handler)
        dispatcher.add_handler(play_handler)

        # unknown handler
        unknown_handler = MessageHandler(Filters.command, unknown)
        dispatcher.add_handler(unknown_handler)

        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO)

        updater.start_polling()


def start(update: Update, context: CallbackContext):
    user_id = get_user(update, context)
    coins = Coins.objects.get(username=user_id)
    text = f"Hi! Welcome to the game!\n" \
           f"Username - {update.effective_chat.username}\n" \
           f"Coins - {coins.coins}"

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text)


# def delete(update: Update, context: CallbackContext):
#     user_id = get_user(update, context)
#     coins = Profile.objects.get(id=user_id[0]).delete()
#     text = "delete"
#
#     context.bot.send_message(
#         chat_id=update.effective_chat.id,
#         text=text)


def play(update: Update, context: CallbackContext):
    try:
        coin_choice, bid = context.args
        bid = int(bid)
        if coin_choice in ("heads", "tails"):
            text = coin_choice.upper()
        else:
            text = WRONG_INPUT_EN

        user_id = get_user(update, context)
        if coin_choice.upper() == random_coin_choice():
            text = WON
            increase_coins(user_id=user_id, bid=bid)
        else:
            reduce_coins(user_id=user_id, bid=bid)
            text = LOST
    except (ValueError, IndexError):
        text = "Wrong input"

    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def unknown(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Sorry, I didn't understand that command.")


def random_coin_choice():
    coins_sides = [HEADS, TAILS]
    computer_choice = random.choice(coins_sides)
    print(computer_choice)
    return computer_choice


def reduce_coins(user_id, bid):
    reducing_factor = 1
    coins_amount = Coins.objects.filter(username_id=user_id).values_list('coins')
    coins_amount2 = coins_amount[0][0] - bid * reducing_factor
    coins_amount.update(coins=coins_amount2)


def increase_coins(user_id, bid):
    reducing_factor = 2
    coins_amount = Coins.objects.filter(username_id=user_id).values_list('coins')
    coins_amount2 = coins_amount[0][0] + bid * reducing_factor
    coins_amount.update(coins=coins_amount2)


def get_user(update, context):

    username = update.effective_chat.username

    # if not username at Telegram
    username = username if username else f'User {update.effective_chat.id}'
    external_id = update.effective_chat.id

    user = Profile.objects.filter(external_id=external_id).values_list('id')
    if user:
        user.update(external_id=external_id, username=username)
        user_id = user[0]
    else:
        user = user.create(external_id=external_id, username=username)
        user_id = user.pk

    return user_id
