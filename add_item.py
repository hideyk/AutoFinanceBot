from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler, CommandHandler, ConversationHandler
from emoji import emojize


FIRST, SECOND = range(2)
EXPENSES = ["🍕:fnb", "💕:date", "🚇:publictransport", "🚕:privatetransport", "🏠:housing", "🏖:travel", "🐶:pet"]
RETURNS = ["📈:investment"]
RECURRING = ["💵:income", "📱:phonebill"]
BACK_BUTTON = [InlineKeyboardButton("🔙", callback_data="back")]


def add_helper(update, context):
    keyboard = [[InlineKeyboardButton("💸", callback_data='💸:expense'),
                 InlineKeyboardButton("💰", callback_data='💰:return'),
                 InlineKeyboardButton("📆", callback_data='📆:recurring')]
                ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        update.message.reply_text(
        "Add a new item?",
        reply_markup=reply_markup
        )
    else:
        update.callback_query.edit_message_text(
            text="Let's try this again",
            reply_markup=reply_markup
        )
    return FIRST


def add_expense(update, context):
    query = update.callback_query
    query.answer()
    keyboard = [[InlineKeyboardButton(x.split(":")[0], callback_data=x) for x in EXPENSES], BACK_BUTTON]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="{} selected".format(query.data),
        reply_markup=reply_markup
    )
    return SECOND


def add_return(update, context):
    query = update.callback_query
    query.answer()
    keyboard = [[InlineKeyboardButton("hi", callback_data="hi"),
                 InlineKeyboardButton("bye", callback_data="bye")],
                BACK_BUTTON]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="{} selected".format(query.data),
        reply_markup=reply_markup
    )
    return SECOND


def add_recurring(update, context):
    query = update.callback_query
    query.answer()
    keyboard = [[InlineKeyboardButton("hi", callback_data="hi"),
                 InlineKeyboardButton("bye", callback_data="bye")],
                BACK_BUTTON]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="{} selected".format(query.data),
        reply_markup=reply_markup
    )
    return SECOND


def add_description(update, context):
    query = update.callback_query
    query.answer()