import requests
from bs4 import BeautifulSoup
from pprint import pprint
from datetime import datetime

class ParseBrochure:
    def __init__(self, page):
        self.req = requests.get(page)
        self.soup = BeautifulSoup(self.req.text, 'html.parser')

    @staticmethod
    def clean_thumbnail(url):
        url = url.get('src') or url.get('data-src')
        if "=" in url and "(65)" in url:
            url = url.split('=')[0] + url.split('(65)')[1]
            url = url.split('.jpg')[0] + '.jpg'
        return url

    @staticmethod
    def format_date(date):
        try:
            date_obj = datetime.strptime(date, "%d.%m.%Y")
            formatted_date = date_obj.strftime("%Y-%m-%d")
        except ValueError:
            formatted_date = date
        return formatted_date

    def parse_brochure(self):
        self.divs = self.soup.find_all('div', class_='brochure-thumb col-xs-6 col-sm-3')
        self.row = self.soup.find_all('div', class_='row row-flex')
        self.answer = []
        for div in self.divs:
            a = div.find('a')
            title = a['title']
            thumbnail = self.clean_thumbnail(div.find('img', alt=title))
            shop_name = a['title'].split()[6]
            valid = div.find('small', class_='hidden-sm').get_text().replace("-", "").split()
            valid_from = self.format_date(" ".join(valid[:-1]))
            valid_to = self.format_date(" ".join(valid[-1:]))
            parsed_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            strong = div.find('strong').get_text()
            self.answer.append({'title': strong, 'thumbnail': thumbnail,
                           "shop_name": shop_name,
                           "valid_from": valid_from, "valid_to": valid_to,
                           "parsed_time": parsed_time})
        return self.answer

page = 'https://www.prospektmaschine.de/hypermarkte/'
parse = ParseBrochure(page)
answer = parse.parse_brochure()
pprint(answer)
