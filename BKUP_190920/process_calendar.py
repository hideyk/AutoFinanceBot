@bot.callback_query_handler(lambda query: query.data.startswith("IGNORE") or query.data.startswith("DAY-MONTH")
                                          or query.data.startswith("PREV-MONTH") or query.data.startswith("NEXT-MONTH")
                                          or query.data == "list_day")
def process_calendar(call):
    selected, date = telegramcalendar.process_calendar_selection(bot, call, user_dict)
    if selected:
        msg = bot.send_message(call.message.chat.id,
                                   text=confirmMessage(call),
                                   reply_markup=confirm_markup,
                                   parse_mode=telegram.ParseMode.MARKDOWN)
        user_dict[call.message.chat.id]["lastAdd"] = msg.message_id
    # query = call.data
    # (action, year, month, day) = telegramcalendar.separate_callback_data(query)
    # curr = dt(int(year), int(month), 1)
    # if action == "IGNORE":
    #     bot.answer_callback_query(callback_query_id=call.id)
    # elif action == "DAY-MONTH":
    #     chosen_date = dt(year=int(year), month=int(month), day=int(day))
    #     user_dict[call.message.chat.id]["datetime"] = chosen_date
    #     chosendt = chosen_date.strftime("%a, %d %b %Y")
    #     bot.edit_message_text(chat_id=call.message.chat.id,
    #                           text="{} selected.".format(chosendt),
    #                           message_id=call.message.message_id)
    #     msg = bot.send_message(call.message.chat.id,
    #                            text=confirmMessage(call),
    #                            reply_markup=confirm_markup,
    #                            parse_mode=telegram.ParseMode.MARKDOWN)
    #     user_dict[call.message.chat.id]["lastAdd"] = msg.message_id
    # elif action == "PREV-MONTH":
    #     premonth, preyear = monthDelta(curr, -1)
    #     reply_text = f"*Shift between months and select a date 📅*"
    #     bot.edit_message_text(
    #         text=reply_text,
    #         chat_id=call.message.chat.id,
    #         message_id=call.message.message_id,
    #         reply_markup=telegramcalendar.create_calendar(int(preyear),int(premonth)),
    #         parse_mode=telegram.ParseMode.MARKDOWN
    #     )
    # elif action == "NEXT-MONTH":
    #     nextmonth, nextyear = monthDelta(curr, 1)
    #     reply_text = f"*Shift between months and select a date 📅*"
    #     bot.edit_message_text(
    #         text=reply_text,
    #         chat_id=call.message.chat.id,
    #         message_id=call.message.message_id,
    #         reply_markup=telegramcalendar.create_calendar(int(nextyear),int(nextmonth)),
    #         parse_mode=telegram.ParseMode.MARKDOWN
    #     )