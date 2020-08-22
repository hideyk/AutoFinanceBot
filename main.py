from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, ConversationHandler
from telegram.utils import helpers
import configparser as cfg
from emoji import emojize
from web_connector import get_qotd
from add_item import add_helper, add_expense, add_return, add_recurring


import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger("AutoFinance Bot")


def get_updater():
    config = cfg.ConfigParser()
    config.read("config.cfg")
    api_token = config.get("creds", "token")
    return Updater(api_token, use_context=True)


def start(update, context):
    user = update.message.from_user
    logger.info("User %s started the conversation.", user.first_name)
    msg = "Welcome to AutoFinance Bot, {}! 🌈⛈🎉🌹🐧😊\n\n".format(user['first_name'])
    msg += "AutoFinance Bot assists you with managing cash flow, helping you focus on a more healthy & prudent " \
           "lifestyle 💰💰💰\n\n"
    msg += "Leave the dirty work to us!"
    update.message.reply_text(msg)


def help_user(update, context):
    user = update.message.from_user
    logger.info("User %s requested help", user.first_name)
    update.message.reply_text("What do you require help with?")
    value = update.message.from_user.first_name + update.message.from_user.username
    update.message.reply_text(value)


def quote_of_the_day(update, context):
    update.message.reply_text(QUOTE+"\n- "+QUOTER)


def go_back(update, context):
    pass


QUOTE, QUOTER = get_qotd()
# Stages
FIRST, SECOND, BACK = range(3)
# Callback data
ONE, TWO, THREE, FOUR = range(4)


def main():

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('add', add_helper)],
        states={
            FIRST: [CallbackQueryHandler(add_expense, pattern="💸:expense$"),
                    CallbackQueryHandler(add_return, pattern="💰:return$"),
                    CallbackQueryHandler(add_recurring, pattern="📆:recurring$")],
            # FIRST: [CallbackQueryHandler(input_type, pattern='^' + str(ONE) + '$')]
            SECOND: [CallbackQueryHandler(add_helper, pattern="back$"),
                     CallbackQueryHandler(add_description, pattern="^expense")]
        },
        fallbacks=[CommandHandler('start', start)],
        per_user=True
    )

    updater = get_updater()
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_user))
    dp.add_handler(CommandHandler("qotd", quote_of_the_day))
    dp.add_handler(conv_handler)
    # dp.add_handler(CommandHandler("input", input_options))
    # dp.add_handler(CallbackQueryHandler(input_button))
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
