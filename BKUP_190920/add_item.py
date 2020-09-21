from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import CallbackQueryHandler, CommandHandler, ConversationHandler
from emoji import emojize

START_OVER, FEATURES, CATEGORY = "", "", ""
END = ConversationHandler.END
EXPENSETYPE, DESCRIPTION, TYPING, VALUE = range(4)
TYPE, DESC = "", ""
EXPENSES = ["🍕:fnb", "💕:date", "🚇:publictransport", "🚕:privatetransport", "🏠:housing", "🏖:travel", "🐶:pet"]
RETURNS = ["📈:investment"]
RECURRING = ["💵:income", "📱:phonebill"]
BACK_BUTTON = [InlineKeyboardButton("🔙", callback_data="back")]
EXIT_BUTTON = [InlineKeyboardButton("🔚", callback_data="exit")]


def add_helper(update, context):
    keyboard = [[InlineKeyboardButton("💸", callback_data='expense'),
                 InlineKeyboardButton("💰", callback_data='return'),
                 InlineKeyboardButton("📆", callback_data='recurring')],
                EXIT_BUTTON
                ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        update.message.reply_text(
            "What shall we add today?",
            reply_markup=reply_markup
        )
    else:
        update.callback_query.edit_message_text(
            text="What shall we do today?",
            reply_markup=reply_markup
        )
    return EXPENSETYPE


def add_expense(update, context):
    update.callback_query.answer()
    keyboard = [[InlineKeyboardButton(x.split(":")[0], callback_data="expense:"+x) for x in EXPENSES], BACK_BUTTON]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.callback_query.edit_message_text(
        text="{} selected. Select a category.".format(update.callback_query.data.split(":")[-1].capitalize()),
        reply_markup=reply_markup
    )
    return DESCRIPTION


def add_return(update, context):
    query = update.callback_query
    query.answer()
    keyboard = [[InlineKeyboardButton(x.split(":")[0], callback_data="return:"+x) for x in RETURNS], BACK_BUTTON]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="{} selected. Select a category.".format(query.data.split(":")[-1].capitalize()),
        reply_markup=reply_markup
    )
    return DESCRIPTION


def add_recurring(update, context):
    query = update.callback_query
    query.answer()
    keyboard = [[InlineKeyboardButton(x.split(":")[0], callback_data="recurring:"+x) for x in RECURRING], BACK_BUTTON]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="{} selected. Select a category.".format(query.data.split(":")[-1].capitalize()),
        reply_markup=reply_markup
    )
    return DESCRIPTION


def add_description(update, context):
    context.user_data[TYPE] = update.callback_query.data
    text = 'Give a short description :'

    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text)

    return TYPING


def save_descrip(update, context):
    """Save input for feature and return to feature selection."""
    context.user_data[DESC] = update.message.data
    # ud = context.user_data
    # ud[FEATURES][ud[CURRENT_FEATURE]] = update.message.text

    return VALUE


def add_value(update, context):
    query = update.callback_query
    query.answer()
    print("hi")