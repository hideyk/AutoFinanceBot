from datetime import datetime as dt, timedelta
import configparser as cfg
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
# from db_connector import insertExpense, insertIncome, insertRecurring
from pg_connector import insertExpense, insertIncome
import telegramcalendar
import telegram
from flask import Flask, request
import os

# try:
#     api_token = os.environ['TG_API_TOKEN']
# except Exception as e:
#     config = cfg.ConfigParser()
#     config.read("config.cfg")
#     api_token = config.get("creds", "token")
api_token = "1205348824:AAEEseJMg68aU9cAkGd2JJDLE_RtVdGmDHY"
bot = telebot.TeleBot(api_token, parse_mode=None)

commands = {  # command description used in the "help" command
    '/start'       : 'send_welcome',
    '/help'        : 'Gives you information about the available commands',
    '/add'         : 'add_handler',
    '/info'        : 'bot_info',
    '/show'        : 'show_menu'
}

def runcommand(method_name, msg):
    possibles = globals().copy()
    possibles.update(locals())
    method = possibles.get(method_name)
    if not method:
         raise NotImplementedError("Method %s not implemented" % method_name)
    method(msg)

user_dict = {}
ADDOPTIONS = [ "Expense 💸:expense", "Income 💰:income", "Recurring 📆:recurring" ]
EXPENSES = ["Dining 🍕:dining", "Dates 💕:dates", "Public transport🚇:public transport",
            "Private transport 🚕:private transport", "Housing 🏠:housing", "Travel 🏖:travel"]
INCOMES = [ "Income 💵:income", "Investment 📈:investment", "Bonus 🎁:bonus", "Commission 💎:commission" ]
PLUS_MINUS = [ "Cash flow in 🔼:plus", "Cash flow out🔽:minus" ]
RECURRING_MINUS = [ "Housing 🏠:housing", "Income 💵:income", "Bills 📱:bills", "Subscriptions 📦:subscriptions", "Insurance 🩹:insurance" ]
RECURRING_PLUS = [ "Income 💵:income" ]
SCHEDULES = [ "Daily:sched_daily", "Weekly:sched_weekly", "Monthly:sched_monthly"]
DATEOPTIONS = [ "Today:tdy_date", "Yesterday:yst_date", "Custom date 📆:custom_calendar" ]
CONFIRMOPTIONS = [ "Yes ✔:confirm_yes", "No ❌:confirm_no", "Back 🔙:confirm_back" ]
SHOWOPTIONS = [ "Summary 📊:show_summary", "List 📋:show_list", "Exit:exit" ]
SUMMARYOPTIONS = [ "By day:summary_day", "By month:summary_month", "By year:summary_year" ]
RECORDLISTOPTIONS = [ "By day:list_day" ]
add_buttons = [InlineKeyboardButton(x.split(":")[0], callback_data=x.split(":")[1]) for x in ADDOPTIONS]
expense_buttons = [InlineKeyboardButton(x.split(":")[0], callback_data="2exp:"+x.split(":")[1]) for x in EXPENSES]
income_buttons = [InlineKeyboardButton(x.split(":")[0], callback_data="2inc:"+x.split(":")[1]) for x in INCOMES]
plusminus_buttons = [InlineKeyboardButton(x.split(":")[0], callback_data="2rec:"+x.split(":")[1]) for x in PLUS_MINUS]
recminus_buttons = [InlineKeyboardButton(x.split(":")[0], callback_data="3rec:"+x.split(":")[1]) for x in RECURRING_MINUS]
recplus_buttons = [InlineKeyboardButton(x.split(":")[0], callback_data="3rec:"+x.split(":")[1]) for x in RECURRING_PLUS]
sched_buttons = [InlineKeyboardButton(x.split(":")[0], callback_data=x.split(":")[1]) for x in SCHEDULES]
date_buttons = [InlineKeyboardButton(x.split(":")[0], callback_data=x.split(":")[1]) for x in DATEOPTIONS]
confirm_buttons = [InlineKeyboardButton(x.split(":")[0], callback_data=x.split(":")[1]) for x in CONFIRMOPTIONS]
show_buttons = [InlineKeyboardButton(x.split(":")[0], callback_data=x.split(":")[1]) for x in SHOWOPTIONS]
summary_buttons = [InlineKeyboardButton(x.split(":")[0], callback_data=x.split(":")[1]) for x in SUMMARYOPTIONS]
record_list_buttons = [InlineKeyboardButton(x.split(":")[0], callback_data=x.split(":")[1]) for x in RECORDLISTOPTIONS]
add_markup = InlineKeyboardMarkup()
add_markup.row_width = 1
add_markup.add(*add_buttons)
exp_markup = InlineKeyboardMarkup()
exp_markup.row_width = 2
exp_markup.add(*expense_buttons)
inc_markup = InlineKeyboardMarkup()
inc_markup.row_width = 2
inc_markup.add(*income_buttons)
plusminus_markup = InlineKeyboardMarkup()
plusminus_markup.row_width = 1
plusminus_markup.add(*plusminus_buttons)
recminus_markup = InlineKeyboardMarkup()
recminus_markup.row_width = 2
recminus_markup.add(*recminus_buttons)
recplus_markup = InlineKeyboardMarkup()
recplus_markup.row_width = 2
recplus_markup.add(*recplus_buttons)
sched_markup = InlineKeyboardMarkup()
sched_markup.row_width = 1
sched_markup.add(*sched_buttons)
date_markup = InlineKeyboardMarkup()
date_markup.row_width = 2
date_markup.add(*date_buttons)
confirm_markup = InlineKeyboardMarkup()
confirm_markup.row_width = 2
confirm_markup.add(*confirm_buttons)
show_markup = InlineKeyboardMarkup()
show_markup.row_width = 2
show_markup.add(*show_buttons)
summary_markup = InlineKeyboardMarkup()
summary_markup.row_width = 1
summary_markup.add(*summary_buttons)
record_list_markup = InlineKeyboardMarkup()
record_list_markup.row_width = 1
record_list_markup.add(*record_list_buttons)


def confirmMessage(call):
    amount = user_dict[call.message.chat.id]['amount']
    datetime = user_dict[call.message.chat.id]['datetime']
    return "*[Confirm entry]*\n" \
              f"Type:                _{user_dict[call.message.chat.id]['type'].capitalize()}_\n" \
              f"Category:        _{user_dict[call.message.chat.id]['category'].capitalize()}_\n" \
              f"Amount:          _${amount:.2f}_\n" \
              f"Description:    _{user_dict[call.message.chat.id]['desc']}_\n" \
              f"Date:                _{datetime.strftime('%a, %d %b %Y')}_\n"


def isValidCurrency(s):
    try:
        a = float(s)
        return False if 1000000 < a <= 0 or (len(s.split(".")[-1]) > 2 and s.split(".")[-1] != s.split(".")[0]) else True
    except:
        return False


def monthDelta(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    return month, year


@bot.message_handler(commands=['start'])
def send_welcome(message):
    msg = "Welcome to AutoFinance Bot, {}! 🌈⛈🎉🌹🐧😊\n\n".format(message.chat.first_name)
    msg += "AutoFinance Bot assists you with managing cash flow, helping you focus on a prudent & healthy " \
           "lifestyle 💰💰💰\n\n"
    msg += ""
    bot.send_message(message.chat.id, msg)


@bot.message_handler(commands=['help'])
def send_welcome(message):
    msg = "Hey {}! 😊\n\n".format(message.chat.first_name)
    msg += "All the commands you need can be found here: "
    msg += "/add Add a new expense or income"
    msg += "/start Describes the bot"
    bot.send_message(message.chat.id, msg)


@bot.message_handler(commands=['show'])
def show_menu(message):
    if message.chat.id not in user_dict.keys():
        user_dict[message.chat.id] = {}
    text = "Hey {}! 😊\n\n".format(message.chat.first_name)
    msg = bot.send_message(message.chat.id, text, reply_markup=show_markup)
    user_dict[message.chat.id]["lastShow"] = msg.message_id


@bot.callback_query_handler(lambda query: query.data == "show_summary")
def show_summary(call):
    user_dict[call.message.chat.id]["show_type"] = "show_summary"
    text = "*[Summary]*\n\n" \
           "Please select the time range of your summary!\n"
    bot.edit_message_text(chat_id=call.message.chat.id,
                          text=text,
                          message_id=call.message.message_id,
                          reply_markup=summary_markup,
                          parse_mode=telegram.ParseMode.MARKDOWN
                          )


# @bot.callback_query_handler(lambda query: query.data == "show_list")
# def show_list(call):


@bot.message_handler(commands=['add'])
def add_handler(message):
    if message.chat.id not in user_dict.keys():
        user_dict[message.chat.id] = {}
    if "lastAdd" in user_dict[message.chat.id].keys():
        bot.edit_message_text(chat_id=message.chat.id,
                              text="New instance of /add started.",
                              message_id=user_dict[message.chat.id]["lastAdd"])
    msg = bot.send_message(message.chat.id, 'What shall we add sir?', reply_markup=add_markup)
    user_dict[message.chat.id]["lastAdd"] = msg.message_id


@bot.callback_query_handler(lambda query: query.data == "expense" or query.data.startswith("2exp"))
def expense_query(call):
    if call.data.startswith("exp"):
        user_dict[call.message.chat.id]["type"] = "expense"
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
        user_dict[call.message.chat.id]["lastAdd"] = msg.message_id
        bot.register_next_step_handler(msg, process_amount)


@bot.callback_query_handler(lambda query: query.data == "income" or query.data.startswith("2inc"))
def income_query(call):
    if call.data.startswith("inc"):
        user_dict[call.message.chat.id]["type"] = "income"
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
        user_dict[call.message.chat.id]["lastAdd"] = msg.message_id
        bot.register_next_step_handler(msg, process_amount)


@bot.callback_query_handler(lambda query: query.data == "recurring" or query.data.startswith("2rec") or query.data.startswith("3rec"))
def recurring_query(call):
    if call.data.startswith("rec"):
        user_dict[call.message.chat.id]["type"] = "recurring"
        bot.edit_message_text(chat_id=call.message.chat.id,
                              text="Please select a recurring type.",
                              message_id=call.message.message_id,
                              reply_markup=plusminus_markup)
    if call.data.startswith("2rec"):
        sign = call.data.split(":")[-1]
        cashflow = "+" if sign.endswith("plus") else "-"
        flow = "Cash flow in" if sign.endswith("plus") else "Cash flow out"
        rec_markup = recplus_markup if sign.endswith("plus") else recminus_markup
        user_dict[call.message.chat.id]["cashflow"] = cashflow
        bot.edit_message_text(chat_id=call.message.chat.id,
                              text="{} selected.\n"
                                   "Please select a category.".format(flow),
                              message_id=call.message.message_id,
                              reply_markup=rec_markup)
    if call.data.startswith("3rec"):
        category = call.data.split(":")[-1]
        user_dict[call.message.chat.id]["category"] = category
        bot.edit_message_text(chat_id=call.message.chat.id,
                              text="{} selected.\n"
                                   "Please select a schedule.".format(category.capitalize()),
                              message_id=call.message.message_id,
                              reply_markup=sched_markup)


@bot.callback_query_handler(lambda query: query.data.startswith("sched"))
def process_schedule(call):
    schedule = call.data.split("_")[-1]
    if schedule == "daily":
        pass
    elif schedule == "weekly":
        pass
    elif schedule == "monthly":
        pass
    bot.edit_message_text(chat_id=call.message.chat.id,
                          text="{} schedule selected".format(schedule.capitalize()),
                          message_id=call.message.message_id)
    user_dict[call.message.chat.id]["schedule"] = schedule
    msg = bot.send_message(call.message.chat.id, text="Please enter an amount.")
    user_dict[call.message.chat.id]["lastAdd"] = msg.message_id
    bot.register_next_step_handler(msg, process_amount)


def process_amount(message):
    amount = message.text
    if amount in commands.keys():
        runcommand(commands[amount], message)
        return
    if not isValidCurrency(amount):
        msg = bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=user_dict[message.chat.id]["lastAdd"],
                                    text=f"Value should be between 0.01 and 1000000.\n"
                                        f"Invalid value: {amount}\n"
                                        f"Please try again: ")
        bot.register_next_step_handler(msg, process_amount)
        return
    bot.edit_message_text(chat_id=message.chat.id,
                          message_id=user_dict[message.chat.id]["lastAdd"],
                          text=f"Valid amount: ${float(amount):.2f}")
    user_dict[message.chat.id]["amount"] = float(amount)
    msg = bot.send_message(message.chat.id, text="Please enter a description.")
    user_dict[message.chat.id]["lastAdd"] = msg.message_id
    bot.register_next_step_handler(msg, process_description)


def process_description(message):
    description = message.text
    if description in commands.keys():
        runcommand(commands[description], message)
        return
    if len(description) >= 50:
        msg = bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=user_dict[message.chat.id]["lastAdd"],
                                    text=f"Description too long: {description}\n"
                                         f"Please try again with less than 50 characters: ")
        bot.register_next_step_handler(msg, process_description)
        return
    bot.edit_message_text(chat_id=message.chat.id,
                          message_id=user_dict[message.chat.id]["lastAdd"],
                          text=f"Description: {description}")
    user_dict[message.chat.id]["desc"] = description
    bot.send_message(message.chat.id, text="Select a date", reply_markup=date_markup)


@bot.callback_query_handler(lambda query: query.data.endswith("date") or query.data == "confirm_back" or query.data == "custom_calendar")
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
    if call.data.endswith("date"):
        user_dict[call.message.chat.id]["datetime"] = now
        chosendt = now.strftime("%a, %d %b %Y")
        bot.edit_message_text(chat_id=call.message.chat.id,
                              text="{} selected.".format(chosendt),
                              message_id=call.message.message_id)

        msg = bot.send_message(call.message.chat.id,
                               text=confirmMessage(call),
                               reply_markup=confirm_markup,
                               parse_mode=telegram.ParseMode.MARKDOWN)
        user_dict[call.message.chat.id]["lastAdd"] = msg.message_id
    elif call.data == "custom_calendar":
        nice_date = now.strftime("%B %Y")
        reply_text = f"     *{nice_date}*     "
        bot.edit_message_text(chat_id=call.message.chat.id,
                              text=reply_text,
                              message_id=call.message.message_id,
                              reply_markup=telegramcalendar.create_calendar(),
                              parse_mode=telegram.ParseMode.MARKDOWN
                              )


@bot.callback_query_handler(lambda query: query.data.startswith("IGNORE") or query.data.startswith("DAY") or query.data.startswith("PREV-MONTH") or query.data.startswith("NEXT-MONTH"))
def process_calendar_selection(call):
    query = call.data
    (action, year, month, day) = telegramcalendar.separate_callback_data(query)
    curr = dt(int(year), int(month), 1)
    if action == "IGNORE":
        bot.answer_callback_query(callback_query_id=call.id)
    elif action == "DAY":
        chosen_date = dt(year=int(year), month=int(month), day=int(day))
        user_dict[call.message.chat.id]["datetime"] = chosen_date
        chosendt = chosen_date.strftime("%a, %d %b %Y")
        bot.edit_message_text(chat_id=call.message.chat.id,
                              text="{} selected.".format(chosendt),
                              message_id=call.message.message_id)
        msg = bot.send_message(call.message.chat.id,
                               text=confirmMessage(call),
                               reply_markup=confirm_markup,
                               parse_mode=telegram.ParseMode.MARKDOWN)
        user_dict[call.message.chat.id]["lastAdd"] = msg.message_id
    elif action == "PREV-MONTH":
        premonth, preyear = monthDelta(curr, -1)
        curdate = dt(year=preyear, month=premonth, day=1)
        nice_date = curdate.strftime("%B %Y")
        reply_text = f"     *{nice_date}*     "
        bot.edit_message_text(
            text=reply_text,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=telegramcalendar.create_calendar(int(preyear),int(premonth)),
            parse_mode=telegram.ParseMode.MARKDOWN
        )
    elif action == "NEXT-MONTH":
        nextmonth, nextyear = monthDelta(curr, 1)
        curdate = dt(year=nextyear, month=nextmonth, day=1)
        nice_date = curdate.strftime("%B %Y")
        reply_text = f"     *{nice_date}*     "
        bot.edit_message_text(
            text=reply_text,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=telegramcalendar.create_calendar(int(nextyear),int(nextmonth)),
            parse_mode=telegram.ParseMode.MARKDOWN
        )


@bot.callback_query_handler(lambda query: query.data in [ "confirm_yes", "confirm_no" ])
def confirm_entry(call):
    confirm = call.data
    if confirm == "confirm_yes":
        input_type = user_dict[call.message.chat.id]["type"]
        if input_type == "expense" or input_type == "income":
            category = user_dict[call.message.chat.id]["category"]
            amount = user_dict[call.message.chat.id]["amount"]
            desc = user_dict[call.message.chat.id]["desc"]
            datetime = user_dict[call.message.chat.id]["datetime"]
            cleandt = datetime.strftime("%Y-%m-%d")
            insertType = "Expense"
            if input_type == "expense":
                insertExpense(call.message.chat.id, category, amount, desc, cleandt)
                insertType = "Expense"
            else:
                insertIncome(call.message.chat.id, category, amount, desc, cleandt)
                insertType = "Income"

            final_msg = f"*[{insertType} successfully added]*\n" \
                        f"Category:       {category.capitalize()}\n" \
                        f"Amount:         ${amount:.2f}\n\n" \
                        f"/add another entry?"
            bot.answer_callback_query(callback_query_id=call.id,
                                      show_alert=True,
                                      text="Entry successfully entered.")
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text=final_msg,
                                  parse_mode=telegram.ParseMode.MARKDOWN)
            user_dict[call.message.chat.id] = {}

            return
        elif input_type == "recurring":
            pass
        '''
        {137906605: {'category': 'fnb', 'value': '3', 'descript': 'jk',
                    'type': 'exp'
                     'datetime': datetime.datetime(2020, 9, 24, 17, 50, 49, 107663)}}
        '''

    elif confirm == "confirm_no":
        bot.edit_message_text(chat_id=call.message.chat.id,
                              text="Entry not added.\n"
                                   "Whenever you're ready!🙇‍♂",
                              message_id=call.message.message_id)
        return


'''
- Include an EXPORT function!

'''

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

# server = Flask(__name__)
# @server.route('/' + api_token, methods=['POST'])
# def getMessage():
#     bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
#     return "!", 200
#
#
# @server.route("/")
# def webhook():
#     bot.remove_webhook()
#     bot.set_webhook(url='https://secure-mountain-19020.herokuapp.com/' + api_token)
#     return "!", 200
#
#
# if __name__ == "__main__":
#     server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))