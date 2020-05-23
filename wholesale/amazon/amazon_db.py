from wholesale.db import Session
from wholesale.db.models import ProductWholesale, ProductAmazon
from wholesale.shops.gross_electronic import shop_name as gross_electronic_shop_name
from wholesale.amazon import amazon_api
from tqdm import tqdm


def update_products(batch, session):
    amazon_products = amazon_api.get_base_data(batch)

    for cur_product in amazon_products:
        old_product = (
            session.query(ProductAmazon)
            .filter_by(ean=cur_product.ean, asin=cur_product.asin)
            .first()
        )
        if old_product is None:
            session.add(cur_product)
        elif old_product != cur_product:
            old_product.price = cur_product.price
            old_product.fees = cur_product.fees
            old_product.category_id = cur_product.category_id
            old_product.salesrank = cur_product.salesrank

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
    update_database(gross_electronic_shop_name)
