from wholesale.db import Session
from wholesale.db.models import ProductWholesale
from wholesale.shops.gross_electronic import shop_name as gross_electronic_shop_name


def update_products(batch, session):
    pass


def update_database(shop_name):
    session = Session()

    batch_size = 5
    cur_batch = []
    for cur_product in session.query(ProductWholesale).filter_by(shop_name=shop_name):
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
