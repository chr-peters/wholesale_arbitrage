from scrapy.crawler import CrawlerRunner
from scrapy.settings import Settings
from twisted.internet import reactor
from wholesale.shops.saraswati.saraswati_scrapy.spiders.saraswati_spider import (
    SaraswatiSpider,
)
import logging


def update_database():
    settings = Settings()
    settings.setmodule("wholesale.shops.saraswati.saraswati_scrapy.settings")

    runner = CrawlerRunner(settings)

    d = runner.crawl(SaraswatiSpider)
    d.addBoth(lambda _: reactor.stop())
    reactor.run()  # the script will block here until the crawling is finished


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    update_database()
