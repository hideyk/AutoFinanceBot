from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import CallbackQueryHandler, CommandHandler, ConversationHandler
from emoji import emojize


FIRST, SECOND, THIRD, VALUE = range(4)
ADD_ITEMS = ["💸", "💰", "📆"]
EXPENSES = ["🍕", "💕", "🚇", "🚕", "🏠", "🏖", "🐶"]
RETURNS = ["📈"]
RECURRING = ["💵", "📱"]
BACK_BUTTON = [InlineKeyboardButton("🔙", callback_data="back")]
EXIT_BUTTON = [InlineKeyboardButton("🔚", callback_data="exit")]


def handle_format(icon_list):
    if len(icon_list) > 3:
        rows = len(icon_list) // 3 + 1
        final_list = [[] for x in range(rows)]
        for idx, icon in enumerate(icon_list):
            row = idx // 3
            final_list[row].append(icon)
        return final_list
    else:
        return list.copy(icon_list)


def add_helper(update, context):
    keyboard = [ADD_ITEMS,
                ["🔚"]
                ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
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
    return FIRST


def add_expense(update, context):
    text = update.message.text
    keyboard = handle_format(EXPENSES)
    keyboard.append(["🔙"])
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    update.message.reply_text(
        text="{} Expense selected. Select a category.".format(text),
        reply_markup=reply_markup
    )
    return SECOND


def add_return(update, context):
    text = update.message.text
    keyboard = handle_format(RETURNS)
    keyboard.append(["🔙"])
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    update.message.reply_text(
        text="{} Return selected. Select a category.".format(text),
        reply_markup=reply_markup
    )
    return SECOND


def add_recurring(update, context):
    text = update.message.text
    keyboard = handle_format(RECURRING)
    keyboard.append(["🔙"])
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    update.message.reply_text(
        text="{} Recurring selected. Select a category.".format(text),
        reply_markup=reply_markup
    )
    return SECOND


def add_value(update, context):
    text = update.message.text
    context.user_data['item'] = text
    keyboard = handle_format(RECURRING)
    keyboard.append(["🔙"])
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    update.message.reply_text(
        text="{} Recurring selected. Select a category.".format(text),
        reply_markup=reply_markup
    )
    return THIRD


def add_description(update, context):
    query = update.callback_query
    query.answer()
    # keyboard = [[ReplyKeyboardButton]]
    return THIRD
