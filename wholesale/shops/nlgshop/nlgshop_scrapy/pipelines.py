# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from wholesale.db import Session
from wholesale.db.models import ProductWholesale


class NlgDatabasePipeline(object):
    def __init__(self):
        self.session = Session()

    def process_item(self, item, spider):

        if item.ean == "":
            return item

        old_product = (
            self.session.query(ProductWholesale)
            .filter_by(shop_name=item.shop_name, ean=item.ean)
            .first()
        )

        if old_product is None:
            self.session.add(item)
            self.session.commit()
        elif not old_product == item:
            old_product.name = item.name
            old_product.price_net = item.price_net
            old_product.age_restriction = item.age_restriction
            self.session.commit()

        return item

    def close_spider(self, spider):
        self.session.close()
