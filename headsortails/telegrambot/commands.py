import random

import telegram
from telegram import Update
from telegram.ext import CallbackContext

from telegrambot.static_text_en import WRONG_INPUT_EN, WON, LOST, TAILS, HEADS
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
            text = "You coins is less then bet"
            context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        if coin_choice in ("heads", "tails"):
            text = coin_choice.upper()
        else:
            text = WRONG_INPUT_EN

        if coin_choice.upper() == random_coin_choice():
            text = WON
            change_coins_amount(user_id, bet, 2)
        else:
            change_coins_amount(user_id, bet, -1)
            text = LOST
        record_new_game(user_id, bet, result=(True if text == WON else False))
    except (ValueError, IndexError):
        text = "Wrong input"

    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def unknown(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Sorry, I didn't understand that command.")


# def restart(update, context):
#     Profile.objects.delete(user=get_user_id(update, context))


def random_coin_choice():
    coins_sides = [HEADS, TAILS]
    computer_choice = random.choice(coins_sides)
    return computer_choice


def change_coins_amount(user_id, bet, reducing_factor):
    """Function to increase or reduce coins"""
    coins_amount = get_coins_by_user(user_id)
    coins_amount2 = coins_amount[0][0] + reducing_factor * bet
    coins_amount.update(coins=coins_amount2)


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

    # if not username at Telegram
    username = username if username else f'User {update.effective_chat.id}'
    return username


def get_leader_dashboard(update: Update, context: CallbackContext):
    top_leaders = Coins.objects.order_by('-coins').values_list('username__username', 'coins')[0:10]
    leaders_str = ""

    max_name_length = max([len(str(item[0])) for item in top_leaders])
    header_indent_length = max_name_length+(max_name_length-6)

    for item in top_leaders:
        leader, coins = item
        leaders_str += f"{leader:{max_name_length}} {coins}\n"

    first_str = f"{'Username':{header_indent_length}} Coins"

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"*{first_str}*\n"
             f"`{leaders_str}`",
        parse_mode=telegram.constants.PARSEMODE_MARKDOWN_V2
    )


def get_info(model, values, update, context):
    info_objects = model.objects.filter(username_id=get_user_id(update, context)).values_list(
        **values)
    info_objects_str = ""


def get_game_history(update: Update, context: CallbackContext):
    game_history = GameHistory.objects.filter(username_id=get_user_id(update, context)).values_list(
        'created_at', 'bet', 'result')

    game_history_str = ""
    indent_length = 12

    for item in game_history:
        created_at, bet, result = item
        created_at = str(created_at)[:10]
        result = "Won" if result else "Lose"
        game_history_str += f"{created_at:{indent_length}}" \
                            f"{bet:{4}}" \
                            f"{result:{30}}"

    first_str = f"{'Date':{indent_length}} " \
                f"{'Bet'} " \
                f"{'Result':{16}}"

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"`{first_str}`\n"
             f"`{game_history_str}`",
        parse_mode=telegram.constants.PARSEMODE_MARKDOWN_V2
    )


def record_new_game(user_id, bet, result):
    GameHistory.objects.create(
        bet=bet,
        result=result,
        username_id=user_id
    )


def get_coins_by_user(user_id):
    coins_amount = Coins.objects.filter(username_id=user_id).values_list('coins')
    return coins_amount
