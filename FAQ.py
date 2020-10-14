
FAQ_messages = {
    "Can anyone access my data?": "Definitely not! Your records are linked to your unique Telegram User ID. ",
    "I changed my number. Will my records still be available to me?":
    "Yes. Data is linked to your Telegram User ID. Changing your number won't cause you to lose your records.",
    "While having a cold one with the lads, I accidentally added a wrong entry. Is it possible to edit it?":
    "There is no way to edit your past records at the moment 😔 This might be available in a future release 🔧",
    "How many daily records do I get to save?":
    "Each free account is entitled to 3 daily records. For access to unlimited entries, "
    "you may upgrade to a Premium Account 💎",
    "What is the meaning of life?": "42.. and pizza"
}

def createFAQmessage():
    message = f"Below are some Frequently Asked Questions you might find helpful 🦉📚...\n\n"
    for question, answer in FAQ_messages.items():
        message += f"Q: *{question}*\nA: {answer}\n\n"
    message += "If you have any queries not covered above, please feel free to ask them in *Give Feedback* 💬\n\n" \
               "We understand this list is far from perfect but we'll strive to improve as we grow! ☺️"
    return message