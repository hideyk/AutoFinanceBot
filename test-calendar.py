import calendar
from datetime import datetime as dt

now = dt.now()
year = now.year
month = now.month
my_calendar = calendar.monthcalendar(year, month)

print(my_calendar)


for week in my_calendar:
    print(week)