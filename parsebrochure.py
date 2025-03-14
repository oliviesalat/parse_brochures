import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json


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
        self.divs = self.soup.find_all('div', class_='brochure-thumb')
        self.row = self.soup.find_all('div', class_='row row-flex')
        self.answer = []
        for div in self.divs:
            a = div.find('a')
            title = a['title']
            thumbnail = self.clean_thumbnail(div.find('img', alt=title))
            shop_name = a['title'].split()[6].strip(',')
            valid = div.find('small', class_='hidden-sm').get_text().replace("-", "").split()
            valid_from = self.format_date(" ".join(valid[:-1]))
            valid_to = self.format_date(" ".join(valid[-1:]))
            parsed_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            answer_title = div.find('strong').get_text()
            self.answer.append({'title': answer_title, 'thumbnail': thumbnail,
                           "shop_name": shop_name,
                           "valid_from": valid_from, "valid_to": valid_to,
                           "parsed_time": parsed_time})
        return self.answer

page = 'https://www.prospektmaschine.de/hypermarkte/'
parse = ParseBrochure(page)
answer = parse.parse_brochure()
answer_json = json.dumps(answer, indent=4, ensure_ascii=False)
with open("brochures.json", "w", encoding="utf-8") as file:
    file.write(answer_json)

