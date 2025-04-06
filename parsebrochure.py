from pprint import pprint

import bs4
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json


class ParserCategory:
    def __init__(self,
                 page: str):
        self.page = page
        self.req = requests.get(page)
        self.soup = BeautifulSoup(self.req.text, 'html.parser')
        self.ul = None
        self.li = None
        self.a = None
        self.list_category = ListCategory(self.page)

    def parse_categories(self):
        self.ul = self.soup.find('ul', {'class': 'list-unstyled categories'})
        self.li = self.ul.find_all('li')
        for li in self.li:
            self.list_category.category_list.append(Category(li.find('a').get('href'), self.page))
        pprint([x.url for x in self.list_category.category_list])


class Category:
    def __init__(self,
                 name: str,
                 page: str):
        self.name = name
        self.url = page.replace('/hypermarkte/', self.name)


class Brochure:
    def __init__(
            self, title: str, thumbnail: str, shop_name: str,
            valid_from: str, valid_to: str, parsed_time: str
    ):
        self.title = title
        self.thumbnail = thumbnail
        self.shop_name = shop_name
        self.valid_from = valid_from
        self.valid_to = valid_to
        self.parsed_time = parsed_time
        self.data = self.to_dict()
        self.category = None

    def to_dict(self) -> dict:
        return {
            'title': self.title,
            'thumbnail': self.thumbnail,
            'shop_name': self.shop_name,
            'valid_from': self.valid_from,
            'valid_to': self.valid_to,
            'parsed_time': self.parsed_time
        }

    def add_data(self,
            data: dict):
        self.data = data

    def set_category(self,
                     category: str):
        self.category = category

    def write_data_to_file(self):
        with open("brochures.json", "a", encoding="utf-8") as file:
            file.write(json.dumps(self.data, indent=4, ensure_ascii=False))
            file.write(", \n")


class ListCategory:
    def __init__(self,
                 page: str):
        self.page = page
        self.category_list = []

    def add_brochure(self,
                     brochure: Brochure):
        self.category_list.append(brochure)


class ListBrochure:
    def __init__(self):
        self.list_brochure = []
        self.list_brochure_data = []

    def add_brochure(self,
                     brochure: Brochure):
        self.list_brochure.append(brochure)

    def add_brochure_data(self,
                          data: dict):
        self.list_brochure_data.append(data)

    def write_data_to_file(self):
        with open("brochures.json", "w", encoding="utf-8") as file:
            file.write(json.dumps(self.list_brochure_data, indent=4, ensure_ascii=False))


class ParserBrochure:
    def __init__(self,
                 list_category: ListCategory):
        self.list_category = list_category


    def parser(self):
        list_brochure = ListBrochure()
        for category in self.list_category.category_list:
            url = category.url
            self.parse_brochure(url, list_brochure)
        list_brochure.write_data_to_file()

    def parse_brochure(self,
                       page: str,
                       list_brochure: ListBrochure):
        req = requests.get(page)
        soup = BeautifulSoup(req.text, 'html.parser')
        divs = soup.find_all('div', class_='brochure-thumb')

        for div in divs:
            a = div.find('a')
            answer_title = a['title']
            img_thumb = div.find('img', alt=answer_title)
            thumbnail = img_thumb.get('src') or img_thumb.get('data-src')
            shop_name = a['title'].split()[6].strip(',')
            valid = div.find('small', class_='hidden-sm').get_text().replace("-", "").split()
            valid_from = self.format_date(" ".join(valid[:-1]))
            valid_to = self.format_date(" ".join(valid[-1:]))
            parsed_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            title = div.find('strong').get_text()
            brochure = Brochure(title=title, thumbnail=thumbnail,
                                shop_name=shop_name, valid_from=valid_from,
                                valid_to=valid_to, parsed_time=parsed_time)
            brochure.set_category(page)
            list_brochure.add_brochure(brochure)
            list_brochure.add_brochure_data(brochure.to_dict())


    @staticmethod
    def format_date(date: str) -> str:
        try:
            date_obj = datetime.strptime(date, "%d.%m.%Y")
            formatted_date = date_obj.strftime("%Y-%m-%d")
        except ValueError:
            formatted_date = date
        return formatted_date


page = 'https://www.prospektmaschine.de/hypermarkte/'
parser_category = ParserCategory(page)
parser_category.parse_categories()
parser_brochure = ParserBrochure(parser_category.list_category)
parser_brochure.parser()
