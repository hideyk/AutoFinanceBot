from datetime import datetime as dt, timedelta
import configparser as cfg
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
# from db_connector import insertExpense, insertIncome, insertRecurring
import telegram

config = cfg.ConfigParser()
config.read("config.cfg")
api_token = config.get("creds", "token")

bot = telebot.TeleBot(api_token, parse_mode=None)

commands = {  # command description used in the "help" command
    '/start'       : 'send_welcome',
    '/help'        : 'Gives you information about the available commands',
    '/sendLongText': 'A test using the \'send_chat_action\' command',
    '/getImage'    : 'A test using multi-stage messages, custom keyboard, and media sending',
    '/add'         : 'message_handler'
}

def runcommand(method_name, msg):
    possibles = globals().copy()
    possibles.update(locals())
    method = possibles.get(method_name)
    if not method:
         raise NotImplementedError("Method %s not implemented" % method_name)
    method(msg)

user_dict = {}
ADDOPTIONS = [ "💸:exp", "💰:inc", "📆:rec" ]
EXPENSES = ["🍕:fnb", "💕:dates", "🚇:public transport", "🚕:private transport", "🏠:housing", "🏖:travel", "🐶:pets"]
INCOMES = [ "💵:income", "📈:investment" ]
RECURRING = [ "💵:income", "📱:phone bill" ]
DATEOPTIONS = [ "Today:tdy_date", "Yesterday:yst_date", "Custom date 📆:custdate" ]
CONFIRMOPTIONS = [ "Yes ✔:confirm_yes", "No ❌:confirm_no", "Back 🔙:confirm_back" ]
add_buttons = [InlineKeyboardButton(x.split(":")[0], callback_data=x.split(":")[1]) for x in ADDOPTIONS]
expense_buttons = [InlineKeyboardButton(x.split(":")[0], callback_data="2exp:"+x.split(":")[1]) for x in EXPENSES]
income_buttons = [InlineKeyboardButton(x.split(":")[0], callback_data="2inc:"+x.split(":")[1]) for x in INCOMES]
date_buttons = [InlineKeyboardButton(x.split(":")[0], callback_data=x.split(":")[1]) for x in DATEOPTIONS]
confirm_buttons = [InlineKeyboardButton(x.split(":")[0], callback_data=x.split(":")[1]) for x in CONFIRMOPTIONS]
add_markup = InlineKeyboardMarkup()
add_markup.row_width = 3
add_markup.add(*add_buttons)
exp_markup = InlineKeyboardMarkup()
exp_markup.row_width = 3
exp_markup.add(*expense_buttons)
inc_markup = InlineKeyboardMarkup()
inc_markup.row_width = 2
inc_markup.add(*income_buttons)
date_markup = InlineKeyboardMarkup()
date_markup.row_width = 2
date_markup.add(*date_buttons)
confirm_markup = InlineKeyboardMarkup()
confirm_markup.row_width = 2
confirm_markup.add(*confirm_buttons)


def isValidCurrency(s):
    try:
        a = float(s)
        return False if 1000000 < a <= 0 or (len(s.split(".")[-1]) > 2 and s.split(".")[-1] != s.split(".")[0]) else True
    except:
        return False


@bot.message_handler(commands=['start'])
def send_welcome(message):
    msg = "Welcome to AutoFinance Bot, {}! 🌈⛈🎉🌹🐧😊\n\n".format(message.chat.first_name)
    msg += "AutoFinance Bot assists you with managing cash flow, helping you focus on a prudent & healthy " \
           "lifestyle 💰💰💰\n\n"
    bot.reply_to(message, msg)


@bot.message_handler(commands=['add'])
def message_handler(message):
    try:
        msg = bot.send_message(message.chat.id, 'What shall we add sir?', reply_markup=add_markup)
    except Exception as e:
        pass


@bot.callback_query_handler(lambda query: query.data == "exp" or query.data.startswith("2exp"))
def handle_query(call):
    if call.data.startswith("exp"):
        user_dict[call.message.chat.id] = {}
        user_dict[call.message.chat.id]["type"] = "exp"
        bot.edit_message_text(chat_id=call.message.chat.id,
                              text="Please select an expense type.",
                              message_id=call.message.message_id,
                              reply_markup=exp_markup)
    if call.data.startswith("2exp"):
        category = call.data.split(":")[-1]
        bot.edit_message_text(chat_id=call.message.chat.id,
                              text="{} selected".format(category.capitalize()),
                              message_id=call.message.message_id)
        user_dict[call.message.chat.id]["category"] = category
        msg = bot.send_message(call.message.chat.id, text="Please enter an amount.")
        user_dict[call.message.chat.id]["last"] = msg.message_id
        bot.register_next_step_handler(msg, process_value)


@bot.callback_query_handler(lambda query: query.data == "inc" or query.data.startswith("2inc"))
def handle_query(call):
    if call.data.startswith("inc"):
        user_dict[call.message.chat.id] = {}
        user_dict[call.message.chat.id]["type"] = "inc"
        bot.edit_message_text(chat_id=call.message.chat.id,
                              text="Please select an income type.",
                              message_id=call.message.message_id,
                              reply_markup=inc_markup)
    if call.data.startswith("2inc"):
        category = call.data.split(":")[-1]
        bot.edit_message_text(chat_id=call.message.chat.id,
                              text="{} selected".format(category.capitalize()),
                              message_id=call.message.message_id)
        user_dict[call.message.chat.id]["category"] = category
        msg = bot.send_message(call.message.chat.id, text="Please enter an amount.")
        user_dict[call.message.chat.id]["last"] = msg.message_id
        bot.register_next_step_handler(msg, process_value)


def process_value(message):
    amount = message.text
    if amount in commands.keys():
        runcommand(commands[amount], message)
        return
    if not isValidCurrency(amount):
        msg = bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=user_dict[message.chat.id]["last"],
                                    text=f"Value should be between 0.01 and 1000000.\n"
                                        f"Invalid value: {amount}\n"
                                        f"Please try again: ")
        bot.register_next_step_handler(msg, process_value)
        return
    bot.edit_message_text(chat_id=message.chat.id,
                          message_id=user_dict[message.chat.id]["last"],
                          text=f"Valid amount: ${float(amount):.2f}")
    user_dict[message.chat.id]["amount"] = float(amount)
    msg = bot.send_message(message.chat.id, text="Please enter a description.")
    user_dict[message.chat.id]["last"] = msg.message_id
    bot.register_next_step_handler(msg, process_description)


def process_description(message):
    description = message.text
    if description in commands.keys():
        runcommand(commands[description], message)
        return
    if len(description) >= 50:
        msg = bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=user_dict[message.chat.id]["last"],
                                    text=f"Description too long: {description}\n"
                                         f"Please try again with less than 50 characters: ")
        bot.register_next_step_handler(msg, process_description)
        return
    bot.edit_message_text(chat_id=message.chat.id,
                          message_id=user_dict[message.chat.id]["last"],
                          text=f"Description: {description}")
    user_dict[message.chat.id]["desc"] = description
    bot.send_message(message.chat.id, text="Select a date", reply_markup=date_markup)


@bot.callback_query_handler(lambda query: query.data.endswith("date") or query.data == "confirm_back")
def process_date(call):
    if call.data == "confirm_back":
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text="Select a date",
                              reply_markup=date_markup)
        return
    now = dt.now()

    if call.data == "yst_date":
        now -= timedelta(days=1)
    if call.data == "custdate":
        pass
    user_dict[call.message.chat.id]["datetime"] = now
    chosendt = now.strftime("%a, %d %b %Y")
    bot.edit_message_text(chat_id=call.message.chat.id,
                          text="{} selected.".format(chosendt),
                          message_id=call.message.message_id)
    bot.send_message(call.message.chat.id, text="Confirm entry?", reply_markup=confirm_markup)


@bot.callback_query_handler(lambda query: query.data in [ "confirm_yes", "confirm_no" ])
def confirm_entry(call):
    confirm = call.data
    if confirm == "confirm_yes":
        input_type = user_dict[call.message.chat.id]["type"]
        if input_type == "exp" or input_type == "inc":
            category = user_dict[call.message.chat.id]["category"]
            amount = user_dict[call.message.chat.id]["amount"]
            desc = user_dict[call.message.chat.id]["desc"]
            datetime = user_dict[call.message.chat.id]["datetime"]
            insertType = "Expense"
            '''
            if input_type == "exp":
                insertExpense(call.message.chat.id, category, amount, desc, datetime)
                insertType = "Expense"
            else:
                insertIncome(call.message.chat.id, category, amount, desc, datetime)
                insertType = "Income"
            '''
            final_msg = f"*[{insertType} successfully added]*\n" \
                        f"Category:       {category.capitalize()}\n" \
                        f"Amount:         ${amount:.2f}"
            bot.answer_callback_query(callback_query_id=call.id,
                                      show_alert=True,
                                      text="Entry successfully entered.")
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text=final_msg,
                                  parse_mode=telegram.ParseMode.MARKDOWN)
            return
        elif input_type == "rec":
            pass
        '''
        {137906605: {'category': 'fnb', 'value': '3', 'descript': 'jk',
                    'type': 'exp'
                     'datetime': datetime.datetime(2020, 9, 24, 17, 50, 49, 107663)}}
        '''

    elif confirm == "confirm_no":
        bot.edit_message_text(chat_id=call.message.chat.id,
                              text="Entry not added.",
                              message_id=call.message.message_id)
        return

'''
For final input into DB

Callback as alert
bot.answer_callback_query(callback_query_id=call.id,
                                   show_alert=True,
                                   text="You Clicked " + call.data + " and key is ")


URL markup
markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Google", url="http://www.google.com"))
        markup.add(types.InlineKeyboardButton("Yahoo", url="http://www.yahoo.com"))
        ret_msg = tb.send_message(CHAT_ID, text, disable_notification=True, reply_markup=markup)
        assert ret_msg.message_id 
'''

bot.polling(none_stop=True)