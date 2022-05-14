import telegram
from telegram import Update
from telegram.ext import CallbackContext


import telegrambot.static_text_en as text_en
import telegrambot.models as models
import telegrambot.utils as utils


def start(update: Update, context: CallbackContext):
    user_id = utils.get_user_id(update, context)

    coins_amount = utils.get_coins_by_user(user_id)
    text = f"Hi! Welcome to the game!\n" \
           f"Username - {utils.get_username(update, context)}\n" \
           f"Coins - {coins_amount}"

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text)


def play(update: Update, context: CallbackContext):
    try:
        user_id = utils.get_user_id(update, context)
        coin_choice, bet = context.args
        bet = int(bet)

        if bet > utils.get_coins_by_user(user_id):
            text = text_en.NOT_ENOUGH_COINS
        elif bet <= 0:
            text = text_en.NEGATIVE_NUMBER
        else:
            if coin_choice not in ("heads", "tails"):
                text = text_en.WRONG_INPUT
                context.bot.send_message(chat_id=update.effective_chat.id, text=text)
                return
            elif coin_choice.upper() == utils.random_coin_choice():
                text = text_en.WON
                utils.change_coins_amount(user_id, bet, 2)
            else:
                utils.change_coins_amount(user_id, bet, -1)
                text = text_en.LOST
            utils.record_new_game(user_id, bet, result=(True if text == text_en.WON else False))
    except (ValueError, IndexError):
        text = text_en.WRONG_INPUT
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def unknown(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=text_en.UNKNOWN_COMMAND)


def get_leader_dashboard(update: Update, context: CallbackContext):
    """Get the 10 best players with the highest number of coins"""
    top_leaders = models.Coins.objects.order_by('-coins').values_list('username__username', 'coins')[0:10]

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
    game_history = models.GameHistory.objects.filter(username_id=utils.get_user_id(
        update, context)).values_list(
        'created_at', 'bet', 'result')

    if check_null_data(game_history, context, update):
        return

    game_history_str = ""
    first_str_align = 12
    second_str_align = 5

    for item in game_history:
        created_at, bet, result = item
        created_at = str(created_at)[:10]  # Get data in 'YYYY-mm-dd' format (use 10 first symbols)
        result = "Won" if result else "Lost"

        text_align = 6 - len(str(bet))  # text_align parameter for the elements alignment

        game_history_str += f"{created_at:{first_str_align}} " \
                            f"{bet}{' '*text_align}" \
                            f"{result}\n"

    header_str = f"{'Date':{first_str_align}} " \
                 f"{'Bet':{second_str_align}} " \
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
        text=text_en.HELP_MESSAGE,
        parse_mode=telegram.constants.PARSEMODE_MARKDOWN_V2
    )


def check_null_data(data, context, update):
    if not data:
        text = text_en.NO_INFO
        context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        return True
    return False
