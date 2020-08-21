import logging

from telegram import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, Filters

# Enable logging
from telegram.utils import helpers

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Define constants that will allow us to reuse the deep-linking parameters.
CHECK_THIS_OUT = 'share'
USING_ENTITIES = 'using-entities-here'
SO_COOL = 'so-cool'


def start(update, context):
    bot = context.bot
    url = helpers.create_deep_linked_url(bot.get_me().username, CHECK_THIS_OUT, group=True)
    text = "Sharing is caring:\n" + url
    update.message.reply_text(text)


def deep_linked_level_1(update, context):
    """Reached through the CHECK_THIS_OUT payload"""
    bot = context.bot
    url = helpers.create_deep_linked_url(bot.get_me().username, SO_COOL)
    text = "Awesome, you just accessed hidden functionality! " \
           " Now let's get back to the private chat."
    keyboard = InlineKeyboardMarkup.from_button(
        InlineKeyboardButton(text='Continue here!', url=url)
    )
    update.message.reply_text(text, reply_markup=keyboard)


def deep_linked_level_2(update, context):
    """Reached through the SO_COOL payload"""
    bot = context.bot
    url = helpers.create_deep_linked_url(bot.get_me().username, USING_ENTITIES)
    text = "You can also mask the deep-linked URLs as links: " \
           "[▶️ CLICK HERE]({}).".format(url)
    update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)


def deep_linked_level_3(update, context):
    """Reached through the USING_ENTITIES payload"""
    payload = context.args
    update.message.reply_text("Congratulations! This is as deep as it gets 👏🏻\n\n"
                              "The payload was: {}".format(payload))


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater("1205348824:AAEEseJMg68aU9cAkGd2JJDLE_RtVdGmDHY", use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # More info on what deep linking actually is (read this first if it's unclear to you):
    # https://core.telegram.org/bots#deep-linking

    # Register a deep-linking handler
    dp.add_handler(CommandHandler("start", deep_linked_level_1, Filters.regex(CHECK_THIS_OUT)))

    # This one works with a textual link instead of an URL
    dp.add_handler(CommandHandler("start", deep_linked_level_2, Filters.regex(SO_COOL)))

    # We can also pass on the deep-linking payload
    dp.add_handler(CommandHandler("start",
                                  deep_linked_level_3,
                                  Filters.regex(USING_ENTITIES),
                                  pass_args=True))
    #
    # Make sure the deep-linking handlers occur *before* the normal /start handler.
    dp.add_handler(CommandHandler("start", start))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()