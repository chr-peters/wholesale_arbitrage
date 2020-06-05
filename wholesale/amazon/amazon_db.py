from wholesale.db import Session
from wholesale.db.models import ProductWholesale, ProductAmazon
from wholesale.shops import gross_electronic, saraswati, berk
from wholesale.amazon import amazon_api
from tqdm import tqdm
import logging


def update_products(batch, session):
    amazon_products = amazon_api.get_base_data(batch)

    batch_size = 20
    cur_batch = []
    for cur_product in amazon_products:
        if len(cur_batch) < batch_size:
            cur_batch.append(cur_product)
        else:
            amazon_api.add_competition_data(cur_batch)
            amazon_api.add_fees(cur_batch)
            cur_batch = [cur_product]
    if len(cur_batch) > 0:
        amazon_api.add_competition_data(cur_batch)
        amazon_api.add_fees(cur_batch)

    for cur_product in amazon_products:
        old_product = (
            session.query(ProductAmazon)
            .filter_by(ean=cur_product.ean, asin=cur_product.asin)
            .first()
        )
        if old_product is None:
            session.add(cur_product)
        elif old_product != cur_product:
            old_product.update(cur_product)

    session.commit()


def update_database(shop_name):
    session = Session()

    batch_size = 5
    cur_batch = []
    query = session.query(ProductWholesale).filter_by(shop_name=shop_name)
    for cur_product in tqdm(query, total=query.count()):
        if len(cur_batch) < batch_size:
            cur_batch.append(cur_product)
        else:
            update_products(cur_batch, session)
            cur_batch = [cur_product]
    if len(cur_batch) > 0:
        update_products(cur_batch, session)

    session.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.CRITICAL)
    update_database(saraswati.shop_name)
    update_database(berk.shop_name)
    update_database(gross_electronic.shop_name)
