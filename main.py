from datetime import datetime as dt, timedelta
import configparser as cfg
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from pg_connector import insertNewUser, insertExpense, insertIncome, showCatalogueDay, getDaySummary, getWeekSummary,\
    getMonthSummary
from FAQ import createFAQmessage
import telegramcalendar
import telegram
import os

try:
    api_token = os.environ['TG_API_TOKEN']
except Exception as e:
    config = cfg.ConfigParser()
    config.read("config.cfg")
    api_token = config.get("creds", "token")

bot = telebot.TeleBot(api_token, parse_mode=None)


commands = {  # command description used in the "help" command
    '/start'       : 'send_welcome',
    '/help'        : 'Gives you information about the available commands',
    '/add'         : 'add_handler',
    '/info'        : 'bot_info',
    '/show'        : 'show_record_menu',
    'Cancel'       : 'show_start_menu'
}

def runcommand(method_name, msg):
    possibles = globals().copy()
    possibles.update(locals())
    method = possibles.get(method_name)
    if not method:
         raise NotImplementedError("Method %s not implemented" % method_name)
    method(msg)


def raise_start_menu(bot, call):
    bot.send_message(chat_id=call.message.chat.id,
                     text="Please select one of the available commands below 🔽",
                     reply_markup=start_menu)


def raise_start_menu_message(bot, message):
    bot.send_message(chat_id=message.chat.id,
                     text="Please select one of the available commands below 🔽",
                     reply_markup=start_menu)


def createFeedbackMessage():
    msg = "*[Page Unavailable]*\n\n" \
          "This feature is currently in development, " \
          "look forward to it in a future release. 👨🏻‍💻\n\n" \
          "In the meantime, you may direct all queries and feedback to @hideyukik. Thank you for your patience!"
    return msg


def createAboutMessage():
    msg = "*About Page*\n\n" \
          "Name               ---     AutoFinance Bot\n" \
          "Version            ---     1.0.0-beta\n" \
          "Initial release ---     16th Oct 2020\n"\
          "Creator            ---     Hideyuki Kanazawa\n" \
          "Github page   ---     https://github.com/hideyukikanazawa"
    return msg


def createDayCatalogueMessage(date, db_day_results):
    message = f"*[{prettydate(date)}]*\n\n"
    if db_day_results:
        counter = 1
        for record in db_day_results:
            message += f"{counter}) {record['category'].capitalize()}     {record['amount']}\n" \
                       f"Description: {record['description'].capitalize()}\n\n"
            counter += 1
    else:
        message += "No records found on this day."
    return message


def createDaySummary(date, chosen_day_result, prev_day_result):
    chosenSum, prevSum, percentChange = 0.0, 0.0, 0.0
    change = ""
    for record in chosen_day_result:
        chosenSum += float(record['total'][1:].replace(",", ""))
    for record in prev_day_result:
        prevSum += float(record['total'][1:].replace(",", ""))
    if chosenSum and prevSum:
        percentChange = (chosenSum - prevSum)/prevSum * 100
    if percentChange > 0:
        change = "increase"
    elif percentChange < 0:
        change = "decrease"
    message = f"*{prettydate(date)}*\n\n"
    message += f"Total spent: *${chosenSum:.2f}*\n"
    if percentChange:
        message += f"This is an approximated *{abs(percentChange):.1f}% {change}* from the previous day - ${prevSum:.2f}\n"
    message += "\nCategory -\n"
    for record in chosen_day_result:
        message += f"{record['category'].capitalize()} - {record['total']}\n"
    return message


def createWeekSummary(date, chosen_week_result, prev_week_result):
    chosenSum, prevSum, percentChange = 0.0, 0.0, 0.0
    change = ""
    for record in chosen_week_result:
        chosenSum += float(record['total'][1:].replace(",", ""))
    for record in prev_week_result:
        prevSum += float(record['total'][1:].replace(",", ""))
    if chosenSum and prevSum:
        percentChange = (chosenSum - prevSum)/prevSum * 100
    if percentChange > 0:
        change = "increase"
    elif percentChange < 0:
        change = "decrease"
    mondayOfWeek = telegramcalendar.get_monday(date)
    sundayOfWeek = telegramcalendar.get_sunday(date)
    message = f"*Week of {shortdate(mondayOfWeek)} - {shortdate(sundayOfWeek)}*\n\n"
    message += f"Total spent: *${chosenSum:.2f}*\n"
    if percentChange:
        message += f"This is an approximated *{abs(percentChange):.1f}% {change}* from the previous week - ${prevSum:.2f}\n"
    message += "\nCategory -\n"
    for record in chosen_week_result:
        message += f"{record['category'].capitalize()} - {record['total']}\n"
    return message


def createMonthSummary(year, month, chosen_month_result, prev_month_result):
    chosenSum, prevSum, percentChange = 0.0, 0.0, 0.0
    change = ""
    date = dt(year=year, month=month, day=1)
    for record in chosen_month_result:
        chosenSum += float(record['total'][1:].replace(",", ""))
    for record in prev_month_result:
        prevSum += float(record['total'][1:].replace(",", ""))
    if chosenSum and prevSum:
        percentChange = (chosenSum - prevSum)/prevSum * 100
    if percentChange > 0:
        change = "increase"
    elif percentChange < 0:
        change = "decrease"
    message = f"*{date.strftime('%b %Y')}*\n\n"
    message += f"Total spent: *${chosenSum:.2f}*\n"
    if percentChange:
        message += f"This is an approximated *{abs(percentChange):.1f}% {change}* from the previous month - ${prevSum:.2f}\n"
    message += "\nCategory -\n"
    for record in chosen_month_result:
        message += f"{record['category'].capitalize()} - {record['total']}\n"
    return message


def createConfirmMessage(call):
    amount = user_dict[call.message.chat.id]['amount']
    datetime = user_dict[call.message.chat.id]['datetime']
    return "*[Confirm entry]*\n" \
              f"Type:                _{user_dict[call.message.chat.id]['type'].capitalize()}_\n" \
                  f"Category:        _{user_dict[call.message.chat.id]['category'].capitalize()}_\n" \
              f"Amount:          _${amount:.2f}_\n" \
              f"Description:    _{user_dict[call.message.chat.id]['desc'].capitalize()}_\n" \
              f"Date:                _{prettydate(datetime)}_\n"


EXIT_BUTTON = InlineKeyboardButton("Cancel", callback_data="exit")
user_dict = {}
ADDOPTIONS = [ "Expense 💸:expense", "Income 💰:income", "Recurring 📆:recurring", "Back:back_to_main_menu" ]
EXPENSES = ["Dining 🍕:dining", "Fitness 🧗:fitness", "Retail 👜:retail", "Dates 💕:dates", "Transport🚇:transport", "Housing 🏠:housing", "Leisure 🏖:leisure",
            "▪️Misc▪️:misc"]
INCOMES = [ "Income 💵:income", "Investment 📈:investment", "Bonus 🎁:bonus", "Commission 💎:commission" ]
PLUS_MINUS = [ "Cash flow in 🔼:plus", "Cash flow out🔽:minus" ]
RECURRING_MINUS = [ "Housing 🏠:housing", "Income 💵:income", "Bills 📱:bills", "Subscriptions 📦:subscriptions", "Insurance 🩹:insurance" ]
RECURRING_PLUS = [ "Income 💵:income" ]
SCHEDULES = [ "Daily:sched_daily", "Weekly:sched_weekly", "Monthly:sched_monthly"]
DATEOPTIONS = [ "Today:tdy_date", "Yesterday:yst_date", "Custom date 📆:custom_calendar" ]
CONFIRMOPTIONS = [ "Yes ✔:confirm_yes", "No ❌:confirm_no", "Back 🔙:confirm_back" ]
SHOWOPTIONS = [ "Summary 📊:show_summary", "Catalogue 📋:show_catalogue", "Back:back_to_main_menu" ]
SUMMARYOPTIONS = [ "Daily:summary_day", "Weekly:summary_week", "Monthly:summary_month" ]
SUMMARYDAYOPTIONS = [ "Select another day:summary_day", "Done:exit" ]
SUMMARYWEEKOPTIONS = [ "Select another week:summary_week", "Done:exit" ]
SUMMARYMONTHOPTIONS = [ "Select another month:summary_month", "Done:exit" ]
RECORDCATALOGUEOPTIONS = [ "By day ☀️:catalogue_day" ]
DAYCATALOGUEOPTIONS = [ "Select another day:catalogue_day", "Done:exit" ]
add_buttons = [InlineKeyboardButton(x.split(":")[0], callback_data=x.split(":")[1]) for x in ADDOPTIONS]
expense_buttons = [InlineKeyboardButton(x.split(":")[0], callback_data="2exp:"+x) for x in EXPENSES]
income_buttons = [InlineKeyboardButton(x.split(":")[0], callback_data="2inc:"+x) for x in INCOMES]
plusminus_buttons = [InlineKeyboardButton(x.split(":")[0], callback_data="2rec:"+x) for x in PLUS_MINUS]
recminus_buttons = [InlineKeyboardButton(x.split(":")[0], callback_data="3rec:"+x.split(":")[1]) for x in RECURRING_MINUS]
recplus_buttons = [InlineKeyboardButton(x.split(":")[0], callback_data="3rec:"+x.split(":")[1]) for x in RECURRING_PLUS]
sched_buttons = [InlineKeyboardButton(x.split(":")[0], callback_data=x.split(":")[1]) for x in SCHEDULES]
date_buttons = [InlineKeyboardButton(x.split(":")[0], callback_data=x.split(":")[1]) for x in DATEOPTIONS]
confirm_buttons = [InlineKeyboardButton(x.split(":")[0], callback_data=x.split(":")[1]) for x in CONFIRMOPTIONS]
show_buttons = [InlineKeyboardButton(x.split(":")[0], callback_data=x.split(":")[1]) for x in SHOWOPTIONS]
summary_buttons = [InlineKeyboardButton(x.split(":")[0], callback_data=x.split(":")[1]) for x in SUMMARYOPTIONS]
summary_day_buttons = [InlineKeyboardButton(x.split(":")[0], callback_data=x.split(":")[1]) for x in SUMMARYDAYOPTIONS]
summary_week_buttons = [InlineKeyboardButton(x.split(":")[0], callback_data=x.split(":")[1]) for x in SUMMARYWEEKOPTIONS]
summary_month_buttons = [InlineKeyboardButton(x.split(":")[0], callback_data=x.split(":")[1]) for x in SUMMARYMONTHOPTIONS]
record_catalogue_buttons = [InlineKeyboardButton(x.split(":")[0], callback_data=x.split(":")[1]) for x in RECORDCATALOGUEOPTIONS]
day_catalogue_buttons = [InlineKeyboardButton(x.split(":")[0], callback_data=x.split(":")[1]) for x in DAYCATALOGUEOPTIONS]
cancel_button = KeyboardButton('Cancel')
add_markup = InlineKeyboardMarkup()
add_markup.row_width = 2
add_markup.add(*add_buttons)
exp_markup = InlineKeyboardMarkup()
exp_markup.row_width = 2
exp_markup.add(*expense_buttons)
exp_markup.add(EXIT_BUTTON)
inc_markup = InlineKeyboardMarkup()
inc_markup.row_width = 2
inc_markup.add(*income_buttons)
inc_markup.add(EXIT_BUTTON)
plusminus_markup = InlineKeyboardMarkup()
plusminus_markup.row_width = 1
plusminus_markup.add(*plusminus_buttons)
plusminus_markup.add(EXIT_BUTTON)
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
summary_day_markup = InlineKeyboardMarkup()
summary_day_markup.row_width = 1
summary_day_markup.add(*summary_day_buttons)
summary_week_markup = InlineKeyboardMarkup()
summary_week_markup.row_width = 1
summary_week_markup.add(*summary_week_buttons)
summary_month_markup = InlineKeyboardMarkup()
summary_month_markup.row_width = 1
summary_month_markup.add(*summary_month_buttons)
record_catalogue_markup = InlineKeyboardMarkup()
record_catalogue_markup.row_width = 1
record_catalogue_markup.add(*record_catalogue_buttons)
day_catalogue_markup = InlineKeyboardMarkup()
day_catalogue_markup.row_width = 1
day_catalogue_markup.add(*day_catalogue_buttons)
cancel_markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
cancel_markup.row(cancel_button)
STARTMENUOPTIONS = [ "Add Entry 🖋", "Show Records 🗃", "FAQ ❓", "Give Feedback 📣", "About Page 🗞" ]
start_menu_buttons = [KeyboardButton(x) for x in STARTMENUOPTIONS]
start_menu = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
start_menu.row(start_menu_buttons[0], start_menu_buttons[1])
start_menu.row(start_menu_buttons[2], start_menu_buttons[3])
start_menu.row(start_menu_buttons[4])


def isValidCurrency(s):
    try:
        a = float(s)
        return False if 1000000 < a <= 0 or (len(s.split(".")[-1]) > 2 and s.split(".")[-1] != s.split(".")[0]) else True
    except:
        return False


def getdbdate(datetime):
    return datetime.strftime("%Y-%m-%d")


def shortdate(datetime):
    return datetime.strftime("%a, %d/%m/%y")


def prettydate(datetime):
    return datetime.strftime("%A, %d %b %Y")


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
    insertNewUser(int(message.chat.id), message.chat.first_name)
    bot.send_message(message.chat.id, msg)


@bot.message_handler(commands=['help'])
def send_help(message):
    msg = "Hey {}! 😊\n\n".format(message.chat.first_name)
    msg += "All the commands you need can be found here: "
    msg += "/add Add a new expense or income"
    msg += "/start Describes the bot"
    bot.send_message(message.chat.id, msg)


@bot.message_handler(regexp="FAQ ❓")
def show_FAQ(message):
    msg = createFAQmessage()
    bot.send_message(message.chat.id,
                     text=msg,
                     reply_markup=start_menu,
                     parse_mode=telegram.ParseMode.MARKDOWN)


@bot.message_handler(regexp="Give Feedback 📣")
def show_feedback(message):
    msg = createFeedbackMessage()
    bot.send_chat_action(message.chat.id, 'typing')
    bot.send_photo(chat_id=message.chat.id,
                   photo=open('dog_in_rain.jpg', 'rb'),
                   caption=msg,
                   parse_mode=telegram.ParseMode.MARKDOWN,
                   reply_markup=start_menu)


@bot.message_handler(regexp="About Page 🗞")
def show_feedback(message):
    msg = createAboutMessage()
    bot.send_chat_action(message.chat.id, 'typing', timeout=2)
    bot.send_message(chat_id=message.chat.id,
                     text=msg,
                     parse_mode=telegram.ParseMode.MARKDOWN,
                     reply_markup=start_menu)


@bot.message_handler(regexp="Show Records 🗃")
@bot.message_handler(commands=['show'])
def show_record_menu(message):
    if message.chat.id not in user_dict.keys():
        user_dict[message.chat.id] = {}
    text = f"Heyo {message.chat.first_name} ⭐️\n\n" \
           f"*Summary* provides an overview of your expenses on a daily, weekly or monthly basis. \n\n" \
           f"*Catalogue* provides a list of records and helps you remember how many satays you munched on cheat day " \
           f"😉 don't worry, its a secret between us.\n\n" \
           f"Stay tuned for more features! 🛠 \n" \
           f"All suggestions for improvement are greatly appreciated, do leave me feedback at @hideyukik 🙆‍♂️\n\n" \
           f"Please select an option below 🔽"
    msg = bot.send_message(message.chat.id, text, reply_markup=show_markup, parse_mode=telegram.ParseMode.MARKDOWN)
    user_dict[message.chat.id]["lastShow"] = msg.message_id


@bot.callback_query_handler(lambda query: query.data == "exit")
def exit(call):
    bot.edit_message_text(chat_id=call.message.chat.id,
                          text="Whenever you're ready!🙇‍♂",
                          message_id=call.message.message_id,
                          parse_mode=telegram.ParseMode.MARKDOWN
    )
    raise_start_menu(bot, call)


@bot.callback_query_handler(lambda query: query.data == "back_to_main_menu")
def back_to_main_menu(call):
    bot.edit_message_text(chat_id=call.message.chat.id,
                          text="Going back in time..",
                          message_id=call.message.message_id,
                          parse_mode=telegram.ParseMode.MARKDOWN
    )
    raise_start_menu(bot, call)


def back_to_main_menu_message(message):
    bot.edit_message_text(chat_id=message.chat.id,
                          text="Going back in time..",
                          message_id=message.message_id,
                          parse_mode=telegram.ParseMode.MARKDOWN
    )
    raise_start_menu_message(bot, message)


@bot.callback_query_handler(lambda query: query.data == "show_summary")
def show_summary(call):
    try:
        user_dict[call.message.chat.id]["show_type"] = "show_summary"
        text = "*Summary 📊*\n\n" \
               "Please select the time range of your summary!\n"
        bot.edit_message_text(chat_id=call.message.chat.id,
                              text=text,
                              message_id=call.message.message_id,
                              reply_markup=summary_markup,
                              parse_mode=telegram.ParseMode.MARKDOWN
        )
    except:
        back_to_main_menu(call)
        return


@bot.callback_query_handler(lambda query: query.data == "summary_day" or query.data == "summary_week"
                                          or query.data == "summary_month")
def show_calendar_day(call):
    try:
        user_dict[call.message.chat.id]["show_type"] = call.data
        if call.data == "summary_day":
            text = "*Shift between months and select a date 📅*"
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  text=text,
                                  message_id=call.message.message_id,
                                  reply_markup=telegramcalendar.create_calendar(prev_action=call.data),
                                  parse_mode=telegram.ParseMode.MARKDOWN
                                  )
        if call.data == "summary_week":
            text = "*Shift between months and select a date to get the whole week 📅*\n"
            text += "Note - Weeks start on Monday"
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  text=text,
                                  message_id=call.message.message_id,
                                  reply_markup=telegramcalendar.create_calendar(prev_action=call.data),
                                  parse_mode=telegram.ParseMode.MARKDOWN
                                  )
        if call.data == "summary_month":
            text = "*Shift between years and select a month 📅*"
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  text=text,
                                  message_id=call.message.message_id,
                                  reply_markup=telegramcalendar.month_calendar(prev_action=call.data),
                                  parse_mode=telegram.ParseMode.MARKDOWN
                                  )
    except:
        back_to_main_menu(call)
        return


@bot.callback_query_handler(lambda query: query.data == "show_catalogue")
def show_catalogue(call):
    try:
        user_dict[call.message.chat.id]["show_type"] = call.data
        text = "*Catalogue 📋*\n\n" \
               "Please select how you want your records to be listed.\n"
        bot.edit_message_text(chat_id=call.message.chat.id,
                              text=text,
                              message_id=call.message.message_id,
                              reply_markup=record_catalogue_markup,
                              parse_mode=telegram.ParseMode.MARKDOWN
        )
    except:
        back_to_main_menu(call)
        return


@bot.callback_query_handler(lambda query: query.data == "catalogue_day")
def show_calendar_day(call):
    try:
        user_dict[call.message.chat.id]["show_type"] = call.data
        text = "*Shift between months and select a date 📅*"
        bot.edit_message_text(chat_id=call.message.chat.id,
                              text=text,
                              message_id=call.message.message_id,
                              reply_markup=telegramcalendar.create_calendar(prev_action=call.data),
                              parse_mode=telegram.ParseMode.MARKDOWN
                              )
    except:
        back_to_main_menu(call)
        return


@bot.message_handler(regexp="Add Entry 🖋")
@bot.message_handler(commands=['add'])
def add_handler(message):
    if message.chat.id not in user_dict.keys():
        user_dict[message.chat.id] = {}
    # if "lastAdd" in user_dict[message.chat.id].keys():
    #     bot.edit_message_text(chat_id=message.chat.id,
    #                           text="New instance of /add started.",
    #                           message_id=user_dict[message.chat.id]["lastAdd"],
    #                           reply_markup=ReplyKeyboardRemove())
    msg = bot.send_message(message.chat.id, 'What shall we add today?', reply_markup=add_markup)
    user_dict[message.chat.id]["lastAdd"] = msg.message_id


@bot.callback_query_handler(lambda query: query.data == "expense" or query.data.startswith("2exp"))
def expense_query(call):
    try:
        if call.data.startswith("exp"):
            user_dict[call.message.chat.id]["type"] = "expense"
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  text="Which category does your expense fall under?",
                                  message_id=call.message.message_id,
                                  reply_markup=exp_markup)
        if call.data.startswith("2exp"):
            calldata, niceCat, category = call.data.split(":")
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  text="{} selected".format(niceCat.capitalize()),
                                  message_id=call.message.message_id)
            user_dict[call.message.chat.id]["category"] = category
            msg = bot.send_message(call.message.chat.id,
                                   text="Please enter an amount 💵",
                                   reply_markup=cancel_markup)
            user_dict[call.message.chat.id]["lastAdd"] = msg.message_id
            bot.register_next_step_handler(msg, process_amount)
    except:
        back_to_main_menu(call)
        return


@bot.callback_query_handler(lambda query: query.data == "income" or query.data.startswith("2inc"))
def income_query(call):
    try:
        if call.data.startswith("inc"):
            user_dict[call.message.chat.id]["type"] = "income"
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  text="Which category does your income fall under?",
                                  message_id=call.message.message_id,
                                  reply_markup=inc_markup)
        if call.data.startswith("2inc"):
            calldata, niceCat, category = call.data.split(":")
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  text="{} selected".format(niceCat.capitalize()),
                                  message_id=call.message.message_id)
            user_dict[call.message.chat.id]["category"] = category
            msg = bot.send_message(call.message.chat.id,
                                   text="Please enter an amount 💵 :",
                                   reply_markup=cancel_markup)
            user_dict[call.message.chat.id]["lastAdd"] = msg.message_id
            bot.register_next_step_handler(msg, process_amount)
    except:
        back_to_main_menu(call)
        return


@bot.callback_query_handler(lambda query: query.data == "recurring" or query.data.startswith("2rec") or query.data.startswith("3rec"))
def recurring_query(call):
    try:
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
    except:
        back_to_main_menu(call)
        return


@bot.callback_query_handler(lambda query: query.data.startswith("sched"))
def process_schedule(call):
    try:
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
        msg = bot.send_message(call.message.chat.id,
                               text="Please enter an amount 💵 :",
                               reply_markup=cancel_markup)
        user_dict[call.message.chat.id]["lastAdd"] = msg.message_id
        bot.register_next_step_handler(msg, process_amount)
    except:
        back_to_main_menu(call)
        return


def process_amount(message):
    try:
        amount = message.text
        if amount in commands.keys():
            runcommand(commands[amount], message)
            return
        if not isValidCurrency(amount):
            msg = bot.send_message(chat_id=message.chat.id,
                                        text=f"Value should be between $0.01 and $1000000.\n"
                                            f"Invalid value: {amount}\n"
                                            f"Please enter an amount again 😅",
                                        reply_markup=cancel_markup)
            ReplyKeyboardMarkup()
            bot.register_next_step_handler(msg, process_amount)
            return
        user_dict[message.chat.id]["amount"] = float(amount)
        msg = bot.send_message(message.chat.id,
                               text=f"*Valid amount: ${float(amount):.2f}*\n\n"
                                    f"Please enter a description 📝",
                               reply_markup=cancel_markup,
                               parse_mode=telegram.ParseMode.MARKDOWN)
        user_dict[message.chat.id]["lastAdd"] = msg.message_id
        bot.register_next_step_handler(msg, process_description)
    except:
        back_to_main_menu_message(message)
        return


def process_description(message):
    try:
        description = message.text
        if description in commands.keys():
            runcommand(commands[description], message)
            return
        if len(description) >= 50:
            msg = bot.send_message(chat_id=message.chat.id,
                                   text=f"*Description too long!* {description}\n\n"
                                        f"Please try again with less than 50 characters 😅",
                                   reply_markup=cancel_markup,
                                   parse_mode=telegram.ParseMode.MARKDOWN)
            bot.register_next_step_handler(msg, process_description)
            return
        bot.send_message(chat_id=message.chat.id,
                         text=f"*Description: {description}*",
                         reply_markup=ReplyKeyboardRemove(),
                         parse_mode=telegram.ParseMode.MARKDOWN)
        user_dict[message.chat.id]["desc"] = description
        bot.send_message(message.chat.id, text="Let's select a date 📅", reply_markup=date_markup)
    except:
        back_to_main_menu_message(message)
        return


@bot.callback_query_handler(lambda query: query.data.endswith("date") or query.data == "confirm_back" or query.data == "custom_calendar")
def process_date(call):
    try:
        if call.data == "confirm_back":
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text="Let's select a date again 📅",
                                  reply_markup=date_markup)
            return
        now = dt.now()
        if call.data == "yst_date":
            now -= timedelta(days=1)
        if call.data.endswith("date"):
            user_dict[call.message.chat.id]["datetime"] = now
            msg = bot.edit_message_text(chat_id=call.message.chat.id,
                                   message_id=call.message.message_id,
                                   text=createConfirmMessage(call),
                                   reply_markup=confirm_markup,
                                   parse_mode=telegram.ParseMode.MARKDOWN)
            user_dict[call.message.chat.id]["lastAdd"] = msg.message_id
        elif call.data == "custom_calendar":
            reply_text = f"*Shift between months and select a date 📅*"
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  text=reply_text,
                                  message_id=call.message.message_id,
                                  reply_markup=telegramcalendar.create_calendar(prev_action=call.data),
                                  parse_mode=telegram.ParseMode.MARKDOWN
                                  )
    except:
        back_to_main_menu(call)
        return


@bot.callback_query_handler(lambda query: query.data.startswith("MONTH-IGNORE") or query.data.startswith("DAY-MONTH")
                                          or query.data.startswith("PREV-MONTH") or query.data.startswith("NEXT-MONTH"))
def process_calendar(call):
    try:
        selected, date, prev_action = telegramcalendar.process_calendar_selection(bot, call, user_dict)
        if selected and prev_action == "custom_calendar":
            msg = bot.edit_message_text(chat_id=call.message.chat.id,
                                        message_id=call.message.message_id,
                                        text=createConfirmMessage(call),
                                        reply_markup=confirm_markup,
                                        parse_mode=telegram.ParseMode.MARKDOWN)
            user_dict[call.message.chat.id]["lastAdd"] = msg.message_id
        if selected and prev_action == "catalogue_day":
            bot.send_chat_action(call.message.chat.id, 'typing', timeout=2)
            results = showCatalogueDay(call.message.chat.id, getdbdate(date))
            reply_text = createDayCatalogueMessage(date, results)
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text=reply_text,
                                  reply_markup=day_catalogue_markup,
                                  parse_mode=telegram.ParseMode.MARKDOWN)
        if selected and prev_action == "summary_day":
            bot.send_chat_action(call.message.chat.id, 'typing', timeout=2)
            chosenDayResult, prevDayResult = getDaySummary(call.message.chat.id, getdbdate(date))
            reply_text = createDaySummary(date, chosenDayResult, prevDayResult)
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text=reply_text,
                                  reply_markup=summary_day_markup,
                                  parse_mode=telegram.ParseMode.MARKDOWN)
        if selected and prev_action == "summary_week":
            bot.send_chat_action(call.message.chat.id, 'typing', timeout=2)
            chosenWeekResult, prevWeekResult = getWeekSummary(call.message.chat.id, getdbdate(date))
            reply_text = createWeekSummary(date, chosenWeekResult, prevWeekResult)
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text=reply_text,
                                  reply_markup=summary_week_markup,
                                  parse_mode=telegram.ParseMode.MARKDOWN)
    except:
        back_to_main_menu(call)
        return


@bot.callback_query_handler(lambda query: query.data.startswith("MONTH-IGNORE") or query.data.startswith("SELECT-MONTH")
                                          or query.data.startswith("PREV-YEAR") or query.data.startswith("NEXT-YEAR"))
def process_calendar(call):
    selected, year, month, prev_action = telegramcalendar.process_month_selection(bot, call, user_dict)
    if selected and prev_action == "summary_month":
        bot.send_chat_action(call.message.chat.id, 'typing', timeout=2)
        chosenMonthResult, prevMonthResult = getMonthSummary(call.message.chat.id, year, month)
        reply_text = createMonthSummary(year, month, chosenMonthResult, prevMonthResult)
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=reply_text,
                              reply_markup=summary_month_markup,
                              parse_mode=telegram.ParseMode.MARKDOWN)


@bot.callback_query_handler(lambda query: query.data in [ "confirm_yes", "confirm_no" ])
def confirm_entry(call):
    try:
        confirm = call.data
        if confirm == "confirm_yes":
            input_type = user_dict[call.message.chat.id]["type"]
            if input_type == "expense" or input_type == "income":
                category = user_dict[call.message.chat.id]["category"]
                amount = user_dict[call.message.chat.id]["amount"]
                desc = user_dict[call.message.chat.id]["desc"]
                datetime = user_dict[call.message.chat.id]["datetime"]
                cleandt = getdbdate(datetime)
                if input_type == "expense":
                    insertExpense(call.message.chat.id, category, amount, desc, cleandt)
                    insertType = "Expense"
                else:
                    insertIncome(call.message.chat.id, category, amount, desc, cleandt)
                    insertType = "Income"

                final_msg = f"*[{insertType} successfully added]*🎉\n" \
                            f"Category:       {category.capitalize()}\n" \
                            f"Amount:         ${amount:.2f}\n" \
                            f"Description:    {desc}\n\n" \
                            f"/add another entry?"
                bot.answer_callback_query(callback_query_id=call.id,
                                          show_alert=True,
                                          text="Entry successfully added 🎉")
                bot.edit_message_text(chat_id=call.message.chat.id,
                                      message_id=call.message.message_id,
                                      text=final_msg,
                                      parse_mode=telegram.ParseMode.MARKDOWN)
                raise_start_menu(bot, call)
                user_dict[call.message.chat.id] = {}

                return
            elif input_type == "recurring":
                pass

        elif confirm == "confirm_no":
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  text="Entry not added.\n"
                                       "Whenever you're ready!🙇‍♂",
                                  message_id=call.message.message_id)
            raise_start_menu(bot, call)
            return
    except:
        back_to_main_menu(call)
        return


@bot.message_handler(func=lambda message: True)
def show_start_menu(message):
    if message.text == "Cancel":
        msg = f"Let's start over 👌\n\n" \
              f"Please select one of the available commands below 🔽"
    else:
        msg = f"Sorry {message.chat.first_name}, we didn't catch that! 🤦🏻‍♂️🤦🏻‍♀️\n\n"
        msg += "Perhaps you could try one of the available commands below 🔽\n\n"
    bot.send_message(message.chat.id,
                     text=msg,
                     reply_markup=start_menu)


'''
- Include an EXPORT function!
'''

'''
For final input into DB

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
