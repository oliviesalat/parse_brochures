import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json


class ParserBrochure:
    def __init__(
        self,
        page: str, list_brochure
    ):
        self.page = page
        self.req = requests.get(page)
        self.soup = BeautifulSoup(self.req.text, 'html.parser')
        self.row = None
        self.divs = None
        self.list_brochure = list_brochure

    @staticmethod
    def clean_thumbnail(
        url: "bs4.element.Tag"
    ) -> str:
        url = url.get('src') or url.get('data-src')
        if "=" in url and "(65)" in url:
            url = url.split('=')[0] + url.split('(65)')[1]
            url = url.split('.jpg')[0] + '.jpg'
        return url

    @staticmethod
    def format_date(
        date: str
    ) -> str:
        try:
            date_obj = datetime.strptime(date, "%d.%m.%Y")
            formatted_date = date_obj.strftime("%Y-%m-%d")
        except ValueError:
            formatted_date = date
        return formatted_date

    def parse_brochure(
            self
    ):
        self.divs = self.soup.find_all('div', class_='brochure-thumb')
        self.row = self.soup.find_all('div', class_='row row-flex')

        for div in self.divs:
            a = div.find('a')
            answer_title = a['title']
            thumbnail = self.clean_thumbnail(div.find('img', alt=answer_title))
            shop_name = a['title'].split()[6].strip(',')
            valid = div.find('small', class_='hidden-sm').get_text().replace("-", "").split()
            valid_from = self.format_date(" ".join(valid[:-1]))
            valid_to = self.format_date(" ".join(valid[-1:]))
            parsed_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            title = div.find('strong').get_text()
            brochure = Brochure(title=title, thumbnail=thumbnail,
                                shop_name=shop_name, valid_from=valid_from,
                                valid_to=valid_to, parsed_time=parsed_time)
            brochure.add_data(brochure.to_dict())
            self.list_brochure.add_brochure(brochure)


class ListBrochure:
    def __init__(
        self, page: str
    ):
        self.page = page
        self.categories = {}
        self.brochure_list = []

    def parse_categories(self):
        pass

    def add_brochure(self, brochure):

        self.brochure_list.append(brochure)


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
        self.data = None
        self.category = None

    def to_dict(
        self
    ) -> dict:
        return {
            'title': self.title,
            'thumbnail': self.thumbnail,
            'shop_name': self.shop_name,
            'valid_from': self.valid_from,
            'valid_to': self.valid_to,
            'parsed_time': self.parsed_time
        }

    def add_data(
            self,
            data: dict
    ):
        self.data = data

    def write_data_to_file(
            self
    ):
        with open("brochures.json", "a", encoding="utf-8") as file:
            file.write(json.dumps(self.data, indent=4, ensure_ascii=False))

    # def __repr__(self):
    #     return f"Brochure(title={self.title!r}, shop_name={self.shop_name!r})"


page = 'https://www.prospektmaschine.de/norma/'
page = 'https://www.prospektmaschine.de/hypermarkte/'
list_brochure = ListBrochure(page)

parser = ParserBrochure(page, list_brochure)
parser.parse_brochure()
