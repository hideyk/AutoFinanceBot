import requests
from lxml import html


def get_qotd():
    qotd_url = r"https://www.brainyquote.com/quote_of_the_day"
    r = requests.get(qotd_url)
    tree = html.fromstring(r.content)
    quote = tree.xpath('/html/body/div[4]/div[4]/div/div/div/div[1]/div/a/text()')
    quoter = tree.xpath('/html/body/div[4]/div[4]/div/div/div/div[1]/div/div/a/text()')
    return quote[0], quoter[0]