# parse_brochures
This project is a Python console script that parses advertising brochures from the store's website Prospektmaschine and downloads a list of currently valid flyers

Requirements:
  Python 3+
  Requests
  BeautifulSoup4

Example Output
[
  {
    "title": "Vorschau von dem Prospekt des Geschäftes Kaufland, gültig ab dem 13.03.2025",
    "thumbnail": "https://eu.leafletscdns.com/thumbor/M0UFd50qXoxZcr2VFXbR7pRdzhY/de/data/41/331071/0.jpg",
    "shop_name": "Kaufland",
    "valid_from": "2025-03-13",
    "valid_to": "2025-03-19",
    "parsed_time": "2025-03-14 10:55:50"
  },
  ...
]
