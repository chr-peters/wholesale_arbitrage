import scrapy

from wholesale.db.models import ProductWholesaleItem
from wholesale import settings
from wholesale.shops import nlgshop
from scrapy.exceptions import CloseSpider
from decimal import Decimal
import json


class NlgshopSpider(scrapy.Spider):
    name = "nlgshop"

    max_pages = 999  # maximum pages per category to scrape products from

    category_urls = {
        "Esoterik": "https://nlgshop.de/factfinder/Search.ff?query=*&channel=nlgshop_de&navigation=true&filterCategoryPathROOT=Esoterik+Gro%C3%9Fhandel&sortSort=desc&format=json",
        "Geschenkartikel": "https://nlgshop.de/factfinder/Search.ff?query=*&channel=nlgshop_de&navigation=true&filterCategoryPathROOT=Geschenkartikelgro%C3%9Fhandel&sortSort=desc&format=json",
        "Haus und Garten": "https://nlgshop.de/factfinder/Search.ff?query=*&channel=nlgshop_de&navigation=true&filterCategoryPathROOT=Haus+%26+Garten&sortSort=desc&format=json",
        "Schmuck": "https://nlgshop.de/factfinder/Search.ff?query=*&channel=nlgshop_de&navigation=true&filterCategoryPathROOT=Schmuck&sortSort=desc&format=json",
        "Spirituelle Kunst": "https://nlgshop.de/factfinder/Search.ff?query=*&channel=nlgshop_de&navigation=true&filterCategoryPathROOT=Spirituelle+Kunst&sortSort=desc&format=json",
        "Raeucherwerk": "https://nlgshop.de/factfinder/Search.ff?query=*&channel=nlgshop_de&navigation=true&filterCategoryPathROOT=R%C3%A4ucherwerk+Gro%C3%9Fhandel&sortSort=desc&format=json",
    }

    def start_requests(self):
        yield scrapy.Request(url="https://nlgshop.de/account", callback=self.login)

    def login(self, response):
        username = settings.NLG_SHOP["USER"]
        password = settings.NLG_SHOP["PASSWORD"]

        yield scrapy.FormRequest.from_response(
            response,
            formname="login",
            formdata={"email_address": username, "password": password},
            callback=self.after_login,
        )

    def after_login(self, response):
        if response.url == "https://nlgshop.de/account?error":
            raise CloseSpider("Authentication failed.")

        # Login successful! Now start scraping with an authenticated session.
        for url in self.category_urls.values():
            yield scrapy.Request(url=url, callback=self.parse)

    # default function to parse a category
    # TODO: Error-Handling
    def parse(self, response):
        data = json.loads(response.text)
        data = data["searchResult"]

        # extract all products
        for record in data["records"]:
            record = record["record"]

            cur_item = ProductWholesaleItem()
            cur_item.shop_name = nlgshop.shop_name
            cur_item.name = record["Name"]
            cur_item.ean = record["ISBN"]
            cur_item.price_net = Decimal(record["Price"])
            cur_item.age_restriction = 0

            yield cur_item

        # get the next batch of products
        next_link = data["paging"]["nextLink"]
        current_page = data["paging"]["currentPage"]
        if next_link is not None and current_page < self.max_pages:
            next_link = next_link["searchParams"]
            next_link = next_link.replace("FACT-Finder", "factfinder")
            yield response.follow(next_link, callback=self.parse)
