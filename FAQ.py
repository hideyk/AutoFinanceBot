
FAQ_messages = {
    "": "",
    "Can anyone access my data?": "Definitely not! Your records are tied to your unique Telegram User ID. ",
    "How many daily records do I get on a free account?":
    "Each free acount is entitled to 3 daily records. If you'd like to have access to unlimited entries, "
    "please upgrade your account to Premium.",
    "What is the meaning of life?": "42"
}

def createFAQmessage():
    message = f"Frequently Asked Questions\n\n"
    for question, answer in FAQ_messages.items():
        message += f"Q: *{question}*\nA: {answer}\n\n"
    message += "If you have any other queries, please feel free to ask them in *Give Feedback*💬"
    return message