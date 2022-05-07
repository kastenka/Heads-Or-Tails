import telegram
from telegram import Update
from telegram.ext import CallbackContext

from telegrambot.static_text_en import (WRONG_INPUT, WON, LOST, TAILS, HEADS, NOT_ENOUGH_COINS,
                                        HELP_MESSAGE, UNKNOWN_COMMAND, NO_INFO)
from telegrambot.models import Coins, Profile, GameHistory

from telegrambot.utils import (get_user_id, get_coins_by_user, change_coins_amount,
                               random_coin_choice, record_new_game, get_username)


def start(update: Update, context: CallbackContext):
    user_id = get_user_id(update, context)
    coins_amount = get_coins_by_user(user_id)
    text = f"Hi! Welcome to the game!\n" \
           f"Username - {get_username(update, context)}\n" \
           f"Coins - {coins_amount}"

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text)


def play(update: Update, context: CallbackContext):
    try:
        user_id = get_user_id(update, context)
        coin_choice, bet = context.args
        bet = int(bet)

        if bet > get_coins_by_user(user_id):
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


def get_leader_dashboard(update: Update, context: CallbackContext):
    """Get the 10 best players with the highest number of coins"""
    top_leaders = Coins.objects.order_by('-coins').values_list('username__username', 'coins')[0:10]

    if check_null_data(top_leaders, context, update):
        return

    leaders_str = ""
    max_name_length = max([len(str(item[0])) for item in top_leaders])  # Get max_name_length to align the text
    header_indent_length = max_name_length+(max_name_length-6)  # Parameter for the header alignment

    for item in top_leaders:
        leader, coins = item
        leaders_str += f"{leader:{max_name_length}} {coins}\n"

    header_str = f"{'Username':{header_indent_length}} " \
                 f"Coins"

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"*{header_str}*\n"
             f"`{leaders_str}`",
        parse_mode=telegram.constants.PARSEMODE_MARKDOWN_V2
    )


def get_game_history(update: Update, context: CallbackContext):
    game_history = GameHistory.objects.filter(username_id=get_user_id(update, context)).values_list(
        'created_at', 'bet', 'result')

    if check_null_data(game_history, context, update):
        return

    game_history_str = ""
    for item in game_history:
        created_at, bet, result = item
        created_at = str(created_at)[:10]  # Get data in 'YYYY-mm-dd' format (use 10 first symbols)
        result = "Won" if result else "Lost"

        text_align = 6 - len(str(bet))  # text_align parameter for the elements alignment

        game_history_str += f"{created_at:{12}} " \
                            f"{bet}{' '*text_align}" \
                            f"{result}\n"

    header_str = f"{'Date':{12}} " \
                 f"{'Bet':{5}} " \
                 f"Result"

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"`{header_str}`\n"
             f"`{game_history_str}`",
        parse_mode=telegram.constants.PARSEMODE_MARKDOWN_V2
    )


def get_help(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=HELP_MESSAGE,
        parse_mode=telegram.constants.PARSEMODE_MARKDOWN_V2
    )


def check_null_data(data, context, update):
    if not data:
        text = NO_INFO
        context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        return True
    return False
