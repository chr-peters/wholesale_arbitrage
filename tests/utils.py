from wholesale.db.models import ProductWholesale, ProductAmazon


def make_dummy_product_wholesale():
    dummy = ProductWholesale(
        id=1,
        shop_name="dummy_shop",
        name="dummy_name",
        ean="1234",
        is_available=True,
        price_net=1.5,
        age_restriction=0,
    )
    return dummy


def make_dummy_product_amazon():
    dummy = ProductAmazon(
        id=1,
        ean="1234",
        asin="abc",
        price=1.5,
        fees_fba=1,
        fees_closing=0,
        fees_total=1,
        fba_offers=1,
        offers=2,
        has_buy_box=True,
        review_count=10,
        rating=5,
        sales30=10,
        sales365=120,
        category_id="dummy_category",
        sales_rank=1000,
    )
    return dummy
