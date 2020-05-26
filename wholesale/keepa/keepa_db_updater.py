from wholesale import keepa
from wholesale.db import Session
from wholesale.db.models import ProductAmazon
from sqlalchemy import func, asc
from tqdm import tqdm


def update_rating_and_sales_info(product, session):
    res = keepa.get_rating_and_sales_info(product.asin)

    if res.get("review_count") is not None:
        product.review_count = res["review_count"]
    if res.get("rating") is not None:
        product.rating = res["rating"]
    if res.get("sales30") is not None:
        product.sales30 = res["sales30"]
    if res.get("sales365") is not None:
        product.sales365 = res["sales365"]

    session.commit()


def update_no_offer_products():
    session = Session()

    sum_offers = (func.sum(ProductAmazon.offers)).label("sum_offers")
    query = (
        session.query(ProductAmazon.ean, sum_offers)
        .group_by(ProductAmazon.ean)
        .having(sum_offers == 0)
    )
    ean_list = [cur_product.ean for cur_product in query]
    query = session.query(ProductAmazon).filter(ProductAmazon.ean.in_(ean_list))
    for cur_product in tqdm(query, total=query.count()):
        update_rating_and_sales_info(cur_product, session)

    session.close()


if __name__ == "__main__":
    update_no_offer_products()
