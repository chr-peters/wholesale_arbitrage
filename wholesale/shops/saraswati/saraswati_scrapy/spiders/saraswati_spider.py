import scrapy


class SaraswatiSpider(scrapy.Spider):
    name = "saraswati"

    start_urls = ["https://www.saraswati.de/"]

    def parse(self, response):
        print(response.request.headers)
