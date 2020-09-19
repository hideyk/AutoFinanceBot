from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, ConversationHandler
import configparser as cfg
from add_item import add_helper, add_expense, add_return, add_recurring, add_description, add_value


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
    id = update.message.from_user.id
    logger.info("User %s started the conversation.", user.first_name)
    msg = "Welcome to AutoFinance Bot, {}! 🌈⛈🎉🌹🐧😊\n\n".format(user['first_name'])
    msg += "AutoFinance Bot assists you with managing cash flow, helping you focus on a prudent & healthy " \
           "lifestyle 💰💰💰\n\n"
    msg += "Leave the dirty work to us!"
    update.message.reply_text(msg)


def help_user(update, context):
    user = update.message.from_user
    logger.info("User %s requested help", user.first_name)
    update.message.reply_text("What do you require help with?")
    value = update.message.from_user.first_name + update.message.from_user.username
    update.message.reply_text(value)


def end_convo(update, context):
    if update.message:
        update.message.reply_text(
            text="Whenever you're ready!🙇‍♂️"
        )
    if not update.message:
        update.callback_query.edit_message_text(
            text="Whenever you're ready!🙇‍♂️\nAll previous instances of /add exited."
        )
    return ConversationHandler.END


def bao(update, context):
    user = update.message.from_user
    update.message.reply_text("BAOOOOOOOOOOOO <3")


# Stages
FIRST, SECOND, THIRD, BACK, VALUE = range(5)
# Callback data
ONE, TWO, THREE, FOUR = range(4)


def main():

    add_handler = ConversationHandler(
        entry_points=[CommandHandler('add', add_helper)],
        states={
            FIRST: [CallbackQueryHandler(add_expense, pattern=".*expense$"),
                    CallbackQueryHandler(add_return, pattern=".*return$"),
                    CallbackQueryHandler(add_recurring, pattern=".*recurring$"),
                    CallbackQueryHandler(end_convo, pattern="exit$")],
            # FIRST: [CallbackQueryHandler(input_type, pattern='^' + str(ONE) + '$')]
            SECOND: [CallbackQueryHandler(add_helper, pattern="back$"),
                     CallbackQueryHandler(add_description, pattern="^expense"),
                     CallbackQueryHandler(add_description)],
            VALUE: [MessageHandler(Filters.text, add_value)]
        },
        fallbacks=[MessageHandler(Filters.command, end_convo)],
        allow_reentry=True,
        per_user=True
    )

    updater = get_updater()
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_user))
    # dp.add_handler(CommandHandler("qotd", quote_of_the_day))
    dp.add_handler(CommandHandler("bao", bao))
    dp.add_handler(add_handler, 1)
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()