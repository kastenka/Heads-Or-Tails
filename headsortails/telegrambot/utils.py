import random

from django.db.models import F

import telegrambot.static_text_en as text_en
import telegrambot.models as models


def random_coin_choice():
    coins_sides = [text_en.HEADS, text_en.TAILS]
    computer_choice = random.choice(coins_sides)
    return computer_choice


def change_coins_amount(user_id, bet, reducing_factor):
    """Function to increase or reduce coins"""
    coins_amount = models.Coins.objects.filter(username_id=user_id)
    coins_amount_new = get_coins_by_user(user_id) + reducing_factor * bet
    coins_amount.update(coins=coins_amount_new)


def get_user_id(update, context):
    external_id = update.effective_chat.id
    user = models.Profile.objects.filter(external_id=external_id).values_list('id')

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


def record_new_game(user_id, bet, result):
    """Function to add the game to the GameHistory table"""
    models.GameHistory.objects.create(
        bet=bet,
        result=result,
        username_id=user_id
    )


def get_coins_by_user(user_id):
    """Get the number of coins by user_id"""
    coins_amount = models.Coins.objects.get(username=user_id)
    return coins_amount.coins


def add_coins(context):
    """Add 150 coins to each account"""
    coins = models.Coins.objects.all().values_list('coins')
    coins_factor = 150
    coins.update(coins=(F('coins') + coins_factor))
