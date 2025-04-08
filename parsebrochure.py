from pprint import pprint

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
from urllib.parse import urljoin


class CategoryParser:
    def __init__(self, page: str):
        self.page = page
        self.req = requests.get(page)
        self.soup = BeautifulSoup(self.req.text, 'html.parser')
        self.ul = None
        self.li = None
        self.a = None
        self.category_collection = CategoryCollection(self.page)

    def parse_categories(self):
        self.ul = self.soup.find('ul', {'class': 'list-unstyled categories'})
        self.li = self.ul.find_all('li')
        for li in self.li:
            self.category_collection.categories.append(Category(li.find('a').get('href'), self.page))
        pprint([x.url for x in self.category_collection.categories])


class Category:
    def __init__(self, name: str, page: str):
        self.name = name
        self.url = urljoin(page, self.name)


class Brochure:
    def __init__(self, title: str, thumbnail: str, shop_name: str,
                 valid_from: str, valid_to: str, parsed_time: str):
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

    def add_data(self, data: dict):
        self.data = data

    def set_category(self, category: str):
        self.category = category

    def write_data_to_file(self):
        with open("brochures.json", "a", encoding="utf-8") as file:
            file.write(json.dumps(self.data, indent=4, ensure_ascii=False))
            file.write(", \n")


class CategoryCollection:
    def __init__(self, page: str):
        self.page = page
        self.categories = []

    def add_brochure(self, brochure: Brochure):
        self.categories.append(brochure)


class BrochureCollection:
    def __init__(self):
        self.brochure_collection = []
        self.brochure_collection_data = []

    def add_brochure(self, brochure: Brochure):
        self.brochure_collection.append(brochure)

    def add_brochure_data(self, data: dict):
        self.brochure_collection_data.append(data)

    def write_data_to_file(self):
        with open("brochures.json", "w", encoding="utf-8") as file:
            file.write(json.dumps(self.brochure_collection_data, indent=4, ensure_ascii=False))


class BrochureParser:
    def __init__(self, category_collection: CategoryCollection):
        self.category_collection = category_collection

    def parser(self):
        brochure_collection = BrochureCollection()
        for category in self.category_collection.categories:
            self.parse_brochure(category.url, brochure_collection)
        brochure_collection.write_data_to_file()

    def parse_brochure(self, page: str, brochure_collection: BrochureCollection):
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
            brochure_collection.add_brochure(brochure)
            brochure_collection.add_brochure_data(brochure.to_dict())

    @staticmethod
    def format_date(date: str) -> str:
        try:
            date_obj = datetime.strptime(date, "%d.%m.%Y")
            formatted_date = date_obj.strftime("%Y-%m-%d")
        except ValueError:
            formatted_date = date
        return formatted_date


url = 'https://www.prospektmaschine.de/hypermarkte/'
parser_category = CategoryParser(url)
parser_category.parse_categories()
parser_brochure = BrochureParser(parser_category.category_collection)
parser_brochure.parser()
