#!/usr/bin/env python3
#
# A library that allows to create an inline calendar keyboard.
# grcanosa https://github.com/grcanosa
#
"""
Base methods for calendar keyboard creation and processing.
"""

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime as dt
import calendar
import telegram


def monthDelta(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    return month, year


def create_callback_data(action, year, month, day, calldata):
    return ";".join([action,str(year),str(month),str(day),calldata])


def create_month_callback(action, year, month, calldata):
    return ";".join([action, str(year), str(month), calldata])


def separate_callback_data(data):
    return data.split(";")


def is_present_month(cur_year, cur_month, year, month):
    return cur_year == year and cur_month == month


def create_calendar(year=None, month=None, prev_action=None):
    now = dt.now()
    curDay, curMonth, curYear = now.day, now.month, now.year
    if year == None: year = now.year
    if month == None: month = now.month
    caldate = dt(year=year, month=month, day=1)
    data_ignore = create_callback_data("DAY-IGNORE", year, month, 0, prev_action)
    keyboard = []
    present_month = is_present_month(curYear, curMonth, year, month)
    #Second row - Week Days
    for day in ["Mo","Tu","We","Th","Fr","Sa","Su"]:
        keyboard.append(InlineKeyboardButton(day,callback_data=data_ignore))

    my_calendar = calendar.monthcalendar(year, month)
    for week in my_calendar:
        for day in week:
            if(day==0):
                keyboard.append(InlineKeyboardButton(" ",callback_data=data_ignore))
            elif day == curDay and present_month:
                keyboard.append(InlineKeyboardButton("*" + str(day) + "*", callback_data=create_callback_data("DAY-MONTH", year, month, day, prev_action)))
            else:
                keyboard.append(InlineKeyboardButton(str(day), callback_data=create_callback_data("DAY-MONTH", year, month, day, prev_action)))

    #Last row - Buttons
    nicedate = caldate.strftime("%b %Y")

    keyboard.append(InlineKeyboardButton("<", callback_data=create_callback_data("PREV-MONTH", year, month, day, prev_action)))
    keyboard.append(InlineKeyboardButton(f"{nicedate}",callback_data=data_ignore))
    keyboard.append(InlineKeyboardButton(">", callback_data=create_callback_data("NEXT-MONTH", year, month, day, prev_action)))

    calendar_markup = InlineKeyboardMarkup()
    calendar_markup.row_width = 7
    calendar_markup.add(*keyboard)
    return calendar_markup


def process_calendar_selection(telebot, call, userDict):
    ret_data = (False,None,None)
    query = call.data
    (action, year, month, day, prev_action) = separate_callback_data(query)
    curr = dt(int(year), int(month), 1)
    if action == "DAY-IGNORE":
        telebot.answer_callback_query(callback_query_id=call.id)
    elif action == "DAY-MONTH":
        chosen_date = dt(year=int(year), month=int(month), day=int(day))
        chosendt = chosen_date.strftime("%a, %d %b %Y")
        userDict[call.message.chat.id]["datetime"] = chosen_date
        telebot.edit_message_text(chat_id=call.message.chat.id,
                              text="{} selected.".format(chosendt),
                              message_id=call.message.message_id)
        ret_data = True, dt(int(year), int(month), int(day)), prev_action
    elif action == "PREV-MONTH":
        premonth, preyear = monthDelta(curr, -1)
        reply_text = f"*Shift between months and select a date 📅*"
        telebot.edit_message_text(
            text=reply_text,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=create_calendar(int(preyear), int(premonth), prev_action),
            parse_mode=telegram.ParseMode.MARKDOWN
        )
    elif action == "NEXT-MONTH":
        nextmonth, nextyear = monthDelta(curr, 1)
        reply_text = f"*Shift between months and select a date 📅*"
        telebot.edit_message_text(
            text=reply_text,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=create_calendar(int(nextyear), int(nextmonth), prev_action),
            parse_mode=telegram.ParseMode.MARKDOWN
        )
    return ret_data


def month_calendar(year=None, prev_action=None):
    now = dt.now()
    curYear = now.year
    if year == None: year = now.year
    data_ignore = create_month_callback("MONTH-IGNORE", year, str(0), prev_action)
    keyboard = []
    for i, month in enumerate(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]):
        keyboard.append(InlineKeyboardButton(month,callback_data=create_month_callback("SELECT-MONTH", year, str(i+1), prev_action)))

    keyboard.append(InlineKeyboardButton("<", callback_data=create_month_callback("PREV-YEAR", year, str(0), prev_action)))
    keyboard.append(InlineKeyboardButton(f"{year}",callback_data=data_ignore))
    keyboard.append(InlineKeyboardButton(">", callback_data=create_month_callback("NEXT-YEAR", year, str(0), prev_action)))

    month_markup = InlineKeyboardMarkup()
    month_markup.row_width = 4
    month_markup.add(*keyboard)
    return month_markup


def process_month_selection(telebot, call, userDict):
    ret_data = (False,None,None,None)
    query = call.data
    (action, year, month, prev_action) = separate_callback_data(query)
    if action == "MONTH-IGNORE":
        telebot.answer_callback_query(callback_query_id=call.id)
    elif action == "SELECT-MONTH":
        chosen_date = dt(year=int(year), month=int(month), day=1)
        chosen_month = chosen_date.strftime("%b %Y")
        userDict[call.message.chat.id]["chosen_month"] = chosen_date
        telebot.edit_message_text(chat_id=call.message.chat.id,
                              text="{} selected.".format(chosen_month),
                              message_id=call.message.message_id)
        ret_data = True, int(year), int(month), prev_action
    elif action == "PREV-YEAR":
        preyear = int(year) - 1
        reply_text = f"*Shift between years and select a month 📅*"
        telebot.edit_message_text(
            text=reply_text,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=month_calendar(int(preyear), prev_action),
            parse_mode=telegram.ParseMode.MARKDOWN
        )
    elif action == "NEXT-YEAR":
        nextyear = int(year) + 1
        reply_text = f"*Shift between years and select a month 📅*"
        telebot.edit_message_text(
            text=reply_text,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=month_calendar(int(nextyear), prev_action),
            parse_mode=telegram.ParseMode.MARKDOWN
        )
    return ret_data