# [AutoFinanceBot](https://t.me/AutoFinanceBot) - Your one-stop solution for finance management


<img src="media/autofinancebot.png" width="600" />

<br>

---


<img src="media/autofinance_inserting_expense.gif" width="230" height="480"/>

---
<br>

## Introduction

### [AutoFinance Bot](https://t.me/AutoFinanceBot) assists you with managing cash flow, helping you focus on a prudent & healthy lifestyle! 


This Telegram bot is a one stop solution for tracking your daily expenses, income, as well as big ticket purchases. There are two options to view your tracked records; the first way is to view them in a concise summary table, the second way in a more detailed catalogue page. 

Additional features include a `Premium Plan` which gives paying users extra functionalities and a `Q&A section` to help out with users' burning questions. There is also a `Give Feedback` (WIP) option allowing users to direct their concerns straight to the developer. 

The python-based service is hosted on Heroku, with a managed PostgreSQL service provided by Heroku as well. 

View the telegram bot [here](https://t.me/AutoFinanceBot)!

<br>

---

## Motivation

The author of this project and his partner felt it was cumbersome to update their daily expenses over excel spreadsheets. They tried finance management mobile apps that provided similar experiences, however that fell short too. Thus one day the author decided to build something different from the ground up. Being integrated into their main networking app of choice, it was seamless to switch between messaging their loved ones and recording their next pizza expense. 

With [more than 500 million active monthly users](https://cybercrew.uk/blog/telegram-statistics), Telegram has a large global footprint in modern networking and is expected to grow at an accelerated pace. Although WhatsApp was the most downloaded app in 2019, Telegram had not reached its peak and is now the [most downloaded non-gaming app worldwide](https://cybercrew.uk/blog/telegram-statistics/).

Telegram stores users' messages and media over their cloud hosting platform instead of locally on the device. This means your conversations can be easily ported to any device, mobile or web. 

This was an important decisive factor as a finance management bot should remain highly available and easily accessible. Moreover, Telegram Bot API's interface is developer-friendly with easy to manipulate RESTful endpoints. 


<br>

---

## Technology stack
Python | Telegram Bot API | PostgreSQL | Heroku
:-------------------------:|:-------------------------:|:-------------------------:|:-------------------------:
<img src="media/python.png" width="100">  |  <img src="media/telegram_bot.png" width="100"> | <img src="media/postgres.png" width="100"> | <img src="media/heroku.png" width="100">


---

## Specifications

### Main service (`main.py`)
The `main.py` file serves as the entrypoint for the Telegram Bot service. Telebot python package was used as a wrapper around the official Telegram bot API service to communicate with the app interface and provide responses to callback and inline queries. 

Core functions of the main service include the following:
- Insert expense
- Insert income
- View daily/weekly/monthly expense summary
- View daily expense catalogue
- Upgrade to premium subscription
- About page
- FAQ section
- Provide feedback

Inline buttons were provided to the user as options to navigate between pages. Callback and inline query handlers were used to handle user response and decide the next course of action. 

One thing to be improved is that the current main service uses a polling mechanism than a webhook mechanism. This results in inefficient communications between the Telegram Bot API service and our main app as many requests are returned with empty responses. Implementing a webhook mechanism ensures we adopt an event-driven approach and facilitates better overall throughput. 

<br>

### pg connector service (`pg_connector.py`)
The `pg_connector.py` file provides helper functions for connectivity between our app and the Heroku postgreSQL database. 

These functions include (but are not limited to) the following:
- Creating new user records upon initial app start-up
- Creating new expense
- Creating new income 
- Updating premium status
- Getting daily/weekly/monthly expenses
- Getting user records

<br>

### Procfile and runtime.txt
`Procfile` specifies heroku specific entrypoint worker configurations to run our `main.py` service.
`runtime.txt' tells heroku which python version to use when spinning up a worker node. 

<br>

---

## Additional GIFs of AutoFinance

### View expense summary
<img src="media/autofinance_view_expense_summary.gif" width="230" height="480"/>

<br>

---

### View expense catalogue
<img src="media/autofinance_view_expense_catalogue.gif" width="230" height="480"/>

<br>

---

### Premium subscription
<img src="media/autofinance_premium_subscription.gif" width="230" height="480"/>

<br>

---

### Misc. features
<img src="media/autofinance_misc.gif" width="230" height="480"/>


---

## References

AutoFinanceBot: https://t.me/AutoFinanceBot

Python Telegram Bot package documentation: https://python-telegram-bot.readthedocs.io/en/stable/

Telegram API official documentation: https://core.telegram.org/

Cybercrew Telegram statistics: https://cybercrew.uk/blog/telegram-statistics/

BusinessOfApps Telegram statistics: https://www.businessofapps.com/data/telegram-statistics/
