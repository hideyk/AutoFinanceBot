from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.utils import helpers
import configparser as cfg
from emoji import emojize


def get_updater():
    config = cfg.ConfigParser()
    config.read("config.cfg")
    api_token = config.get("creds", "token")
    return Updater(api_token, use_context=True)


def start(update, context):
    user = update.message.from_user
    msg = "Welcome to AutoFinance Bot, {}! 🌈⛈🎉🌹🐧😊\n\n".format(user['first_name'])
    msg += "AutoFinance Bot assists you with managing cash flow, helping you focus on a more healthy & prudent " \
           "lifestyle 💰💰💰\n\n"
    msg += "Leave the dirty work to us!"
    update.message.reply_text(msg)



def help(update, context):
    update.message.reply_text("What do you require help with?")
    value = update.message.from_user.first_name + update.message.from_user.username
    update.message.reply_text(value)


def main():
    updater = get_updater()
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()