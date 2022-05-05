import datetime
import random

import telegram
from django.db.models import F
from telegram import Update
from telegram.ext import CallbackContext

from telegram.ext import JobQueue as job

from telegrambot.static_text_en import (
    WRONG_INPUT,
    WON,
    LOST,
    TAILS,
    HEADS,
    NOT_ENOUGH_COINS,
    HELP_MESSAGE,
    UNKNOWN_COMMAND
)
from telegrambot.models import Coins, Profile, GameHistory


def start(update: Update, context: CallbackContext):
    user_id = get_user_id(update, context)
    coins = Coins.objects.get(username=user_id)
    text = f"Hi! Welcome to the game!\n" \
           f"Username - {update.effective_chat.username}\n" \
           f"Coins - {coins.coins}"

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text)


def play(update: Update, context: CallbackContext):
    try:
        user_id = get_user_id(update, context)
        coin_choice, bet = context.args
        bet = int(bet)

        if bet > get_coins_by_user(user_id)[0][0]:
            text = NOT_ENOUGH_COINS
            context.bot.send_message(chat_id=update.effective_chat.id, text=text)
            return

        if coin_choice not in ("heads", "tails"):
            text = WRONG_INPUT

        if coin_choice.upper() == random_coin_choice():
            text = WON
            change_coins_amount(user_id, bet, 2)
        else:
            change_coins_amount(user_id, bet, -1)
            text = LOST
        record_new_game(user_id, bet, result=(True if text == WON else False))
    except (ValueError, IndexError):
        text = WRONG_INPUT
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def unknown(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=UNKNOWN_COMMAND)


def random_coin_choice():
    coins_sides = [HEADS, TAILS]
    computer_choice = random.choice(coins_sides)
    return computer_choice


def change_coins_amount(user_id, bet, reducing_factor):
    """Function to increase or reduce coins"""
    coins_amount = get_coins_by_user(user_id)
    coins_amount_new = coins_amount[0][0] + reducing_factor * bet
    coins_amount.update(coins=coins_amount_new)


def get_user_id(update, context):
    external_id = update.effective_chat.id
    user = Profile.objects.filter(external_id=external_id).values_list('id')

    if user:
        user.update(external_id=external_id, username=get_username(update, context))
        user_id = user[0][0]
    else:
        user = user.create(external_id=external_id, username=get_username(update, context))
        user_id = user.pk
    return user_id


def get_username(update, context):
    username = update.effective_chat.username

    # If the username doesn't exist in telegram
    username = username if username else f'User {update.effective_chat.id}'
    return username


def get_leader_dashboard(update: Update, context: CallbackContext):
    """ Get the 10 best players with the highest number of coins """
    top_leaders = Coins.objects.order_by('-coins').values_list('username__username', 'coins')[0:10]
    leaders_str = ""

    max_name_length = max([len(str(item[0])) for item in top_leaders])  # get max_name_length to align the text
    header_indent_length = max_name_length+(max_name_length-6)  # A parameter for the headline alignment

    for item in top_leaders:
        leader, coins = item
        leaders_str += f"{leader:{max_name_length}} {coins}\n"

    header_str = f"{'Username':{header_indent_length}} Coins"

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"*{header_str}*\n"
             f"`{leaders_str}`",
        parse_mode=telegram.constants.PARSEMODE_MARKDOWN_V2
    )


def get_game_history(update: Update, context: CallbackContext):
    game_history = list(GameHistory.objects.filter(username_id=get_user_id(update, context)).values_list(
        'created_at', 'bet', 'result'))
    game_history_str = ""
    headers = ('Date', 'Bet', 'Result')

    for item in game_history:
        created_at, bet, result = item
        created_at = str(created_at)[:10]  # get data in 'YYYY-mm-dd' format
        result = "Won" if result else "Lost"

        game_history_str += f"{created_at:{12}}" \
                            f"{bet:{5}}  " \
                            f"{result:{4}}\n"
    headers_str = f"{headers[0]:{14}} {headers[1]:{5}} {headers[2]:{4}}"

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"`{headers_str}`\n"
             f"`{game_history_str}`",
        parse_mode=telegram.constants.PARSEMODE_MARKDOWN_V2
    )


def record_new_game(user_id, bet, result):
    """Function to add the game to the GameHistory table"""
    GameHistory.objects.create(
        bet=bet,
        result=result,
        username_id=user_id
    )


def get_coins_by_user(user_id):
    """To get the number of coins via user_id"""
    coins_amount = Coins.objects.filter(username_id=user_id).values_list('coins')
    return coins_amount


def get_help(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=HELP_MESSAGE,
        parse_mode=telegram.constants.PARSEMODE_MARKDOWN_V2
    )


def add_coins(context):
    """Add 150 coins to each account"""
    coins = Coins.objects.all().values_list('coins')
    coins_factor = 150
    coins.update(coins=(F('coins') + coins_factor))
