import scrapy
from scrapy.exceptions import CloseSpider
import urllib
from wholesale import settings
from wholesale.shops import saraswati
from bs4 import BeautifulSoup
from wholesale.db.models import ProductWholesaleItem
from decimal import Decimal


class SaraswatiSpider(scrapy.Spider):
    name = "saraswati"

    start_urls = ["https://www.saraswati.de/"]
    all_products_url = "https://www.saraswati.de/product-all.php?count=200"  # count=200 displays 200 products per page

    def parse(self, response):
        return scrapy.FormRequest.from_response(
            response,
            formid="loginbox",
            formdata={
                "login_email_address": settings.SARASWATI["USER"],
                "login_password": settings.SARASWATI["PASSWORD"],
            },
            callback=self.after_login,
        )

    def after_login(self, response):
        if urllib.parse.urlsplit(response.url).path == "/anmeldung/":
            raise CloseSpider("Authentication failed.")
        return response.follow(self.all_products_url, callback=self.parse_product_page)

    def parse_product_page(self, response):
        bs = BeautifulSoup(response.text, "html.parser")
        product_containers = bs.find_all("article", attrs={"class": "product"})
        for cur_product in product_containers:
            cur_name = cur_product.find(
                "a", attrs={"class": "card-title"}
            ).string.strip()

            ean_tag = cur_product.find("dt", string="GTIN")
            if ean_tag is None:
                continue
            cur_ean = ean_tag.next_sibling.next_sibling.string.strip()
            cur_ean = cur_ean.replace("ISBN", "")
            cur_ean = cur_ean.replace("-", "")
            cur_ean = cur_ean.strip()

            price_string = list(
                cur_product.find("div", attrs={"class": "theprice"}).stripped_strings
            )[0]
            cur_price = Decimal(
                price_string.replace("EUR", "").replace(",", ".").strip()
            )

            yield ProductWholesaleItem(
                shop_name=saraswati.shop_name,
                name=cur_name,
                ean=cur_ean,
                price_net=cur_price,
            )

        next_link = bs.find("a", attrs={"rel": "next"})
        if next_link is not None:
            yield response.follow(next_link["href"], callback=self.parse_product_page)
