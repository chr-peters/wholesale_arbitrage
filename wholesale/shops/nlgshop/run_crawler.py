from scrapy.crawler import CrawlerRunner
from scrapy.settings import Settings
from wholesale.shops.nlgshop.nlgshop_scrapy.spiders.nlgshop_spider import NlgshopSpider
from twisted.internet import reactor


def update_database():
    settings = Settings()
    settings.setmodule("wholesale.shops.nlgshop.nlgshop_scrapy.settings")

    runner = CrawlerRunner(settings)

    d = runner.crawl(NlgshopSpider)
    d.addBoth(lambda _: reactor.stop())
    reactor.run()  # the script will block here until the crawling is finished


if __name__ == "__main__":
    update_database()
