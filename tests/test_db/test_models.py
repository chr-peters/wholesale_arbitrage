from wholesale.db.models import ProductWholesale, ProductWholesaleItem
from tests.utils import make_dummy_product_amazon, make_dummy_product_wholesale


def test_product_wholesale_table_name():
    dummy = make_dummy_product_wholesale()
    assert dummy.__tablename__ == "products_wholesale"


def test_product_wholesale_has_attrs():
    dummy = make_dummy_product_wholesale()
    dummy_attrs = set(dummy.__class__.__dict__.keys())
    assert dummy_attrs == {
        "__module__",
        "__tablename__",
        "id",
        "shop_name",
        "name",
        "ean",
        "is_available",
        "price_net",
        "age_restriction",
        "timestamp_created",
        "timestamp_updated",
        "update",
        "__eq__",
        "__repr__",
        "__str__",
        "__doc__",
        "__hash__",
        "__table__",
        "_sa_class_manager",
        "__init__",
        "__mapper__",
    }


def test_product_wholesale_string():
    dummy = make_dummy_product_wholesale()

    dummy_string = str(dummy)

    assert (
        dummy_string == "ProductWholesale("
        "id=1, "
        "shop_name='dummy_shop', "
        "name='dummy_name', "
        "ean='1234', "
        "is_available=True, "
        "price_net=1.5, "
        "age_restriction=0, "
        "timestamp_created=None, "
        "timestamp_updated=None"
        ")"
    )


def test_product_wholesale_eq():
    dummy = make_dummy_product_wholesale()
    another = make_dummy_product_wholesale()

    assert dummy == another

    # id is not compared in ProductWholesale.__eq__
    another.id = 2
    assert dummy == another
    another.id = 1

    another.shop_name = "test"
    assert dummy != another
    another.shop_name = "dummy_shop"
    assert dummy == another

    another.name = "test"
    assert dummy != another
    another.name = "dummy_name"
    assert dummy == another

    another.ean = "12"
    assert dummy != another
    another.ean = "1234"
    assert dummy == another

    another.is_available = False
    assert dummy != another
    another.is_available = True
    assert dummy == another

    another.price_net = 0
    assert dummy != another
    another.price_net = 1.5
    assert dummy == another

    another.age_restriction = 18
    assert dummy != another
    another.age_restriction = 0
    assert dummy == another


def test_product_wholesale_update():
    dummy = make_dummy_product_wholesale()
    another = make_dummy_product_wholesale()

    dummy.update(another)
    assert dummy == another

    another.name = "test"
    dummy.update(another)
    assert dummy.name == "test"

    another.is_available = False
    dummy.update(another)
    assert dummy.is_available is False

    another.price_net = 1.4
    dummy.update(another)
    assert dummy.price_net == 1.4

    another.age_restriction = 18
    dummy.update(another)
    assert dummy.age_restriction == 18

    assert dummy == another


def test_product_wholesale_update_none():
    dummy = make_dummy_product_wholesale()
    another = make_dummy_product_wholesale()

    another.name = None
    dummy.update(another)
    assert dummy.name is not None

    another.is_available = None
    dummy.update(another)
    assert dummy.is_available is not None

    another.price_net = None
    dummy.update(another)
    assert dummy.price_net is not None

    another.age_restriction = None
    dummy.update(another)
    assert dummy.age_restriction is not None


def test_product_wholesale_item():
    test_item = ProductWholesaleItem()

    assert isinstance(test_item, dict) is True
    assert isinstance(test_item, ProductWholesale) is True


def test_product_amazon_table_name():
    dummy = make_dummy_product_amazon()
    assert dummy.__tablename__ == "products_amazon"


def test_product_wholesale_has_attrs():
    dummy = make_dummy_product_amazon()
    dummy_attrs = set(dummy.__class__.__dict__.keys())
    assert dummy_attrs == {
        "timestamp_created",
        "fees_fba",
        "__hash__",
        "sales_rank",
        "_sa_class_manager",
        "update",
        "sales30",
        "sales365",
        "timestamp_updated",
        "__module__",
        "rating",
        "__table__",
        "fees_closing",
        "ean",
        "fees_total",
        "asin",
        "price",
        "__mapper__",
        "__repr__",
        "__str__",
        "id",
        "__doc__",
        "__init__",
        "__eq__",
        "__tablename__",
        "has_buy_box",
        "fba_offers",
        "offers",
        "review_count",
        "category_id",
    }


def test_product_amazon_string():
    dummy = make_dummy_product_amazon()
    dummy_string = str(dummy)

    assert (
        dummy_string == "ProductAmazon("
        "id=1, "
        "ean='1234', "
        "asin='abc', "
        "price=1.5, "
        "fees_fba=1, "
        "fees_closing=0, "
        "fees_total=1, "
        "fba_offers=1, "
        "offers=2, "
        "has_buy_box=True, "
        "review_count=10, "
        "rating=5, "
        "sales30=10, "
        "sales365=120, "
        "category_id='dummy_category', "
        "sales_rank=1000, "
        "timestamp_created=None, "
        "timestamp_updated=None"
        ")"
    )


def test_product_amazon_eq():
    dummy = make_dummy_product_amazon()
    another = make_dummy_product_amazon()

    assert dummy == another

    another.ean = "test"
    assert dummy != another
    another.ean = "1234"
    assert dummy == another

    another.asin = "test"
    assert dummy != another
    another.asin = "abc"
    assert dummy == another

    another.price = 0
    assert dummy != another
    another.price = 1.5
    assert dummy == another

    another.fees_fba = 5
    assert dummy != another
    another.fees_fba = 1
    assert dummy == another

    another.fees_closing = 10
    assert dummy != another
    another.fees_closing = 0
    assert dummy == another

    another.fees_total = 20
    assert dummy != another
    another.fees_total = 1
    assert dummy == another

    another.fba_offers = 10
    assert dummy != another
    another.fba_offers = 1
    assert dummy == another

    another.offers = 5
    assert dummy != another
    another.offers = 2
    assert dummy == another

    another.has_buy_box = False
    assert dummy != another
    another.has_buy_box = True
    assert dummy == another

    another.review_count = 0
    assert dummy != another
    another.review_count = 10
    assert dummy == another

    another.rating = 1
    assert dummy != another
    another.rating = 5
    assert dummy == another

    another.sales30 = 50
    assert dummy != another
    another.sales30 = 10
    assert dummy == another

    another.sales365 = 10
    assert dummy != another
    another.sales365 = 120
    assert dummy == another

    another.category_id = "test"
    assert dummy != another
    another.category_id = "dummy_category"
    assert dummy == another

    another.sales_rank = 500
    assert dummy != another
    another.sales_rank = 1000
    assert dummy == another


def test_product_amazon_update():
    dummy = make_dummy_product_amazon()
    another = make_dummy_product_amazon()

    another.price = 2
    dummy.update(another)
    assert dummy.price == 2
    dummy.price = 1.5
    another.price = 1.5
    assert dummy == another

    another.fees_fba = 10
    dummy.update(another)
    assert dummy.fees_fba == 10
    dummy.fees_fba = 1
    another.fees_fba = 1
    assert dummy == another

    another.fees_closing = 20
    dummy.update(another)
    assert dummy.fees_closing == 20
    dummy.fees_closing = 0
    another.fees_closing = 0
    assert dummy == another

    another.fees_total = 5
    dummy.update(another)
    assert dummy.fees_total == 5
    dummy.fees_total = 1
    another.fees_total = 1
    assert dummy == another

    another.fba_offers = 10
    dummy.update(another)
    assert dummy.fba_offers == 10
    dummy.fba_offers = 1
    another.fba_offers = 1
    assert dummy == another

    another.offers = 10
    dummy.update(another)
    assert dummy.offers == 10
    dummy.offers = 2
    another.offers = 2
    assert dummy == another

    another.has_buy_box = False
    dummy.update(another)
    assert dummy.has_buy_box is False
    dummy.has_buy_box = True
    another.has_buy_box = True
    assert dummy == another

    another.review_count = 0
    dummy.update(another)
    assert dummy.review_count == 0
    dummy.review_count = 10
    another.review_count = 10
    assert dummy == another

    another.rating = 0
    dummy.update(another)
    assert dummy.rating == 0
    dummy.rating = 5
    another.rating = 5
    assert dummy == another

    another.sales30 = 500
    dummy.update(another)
    assert dummy.sales30 == 500
    dummy.sales30 = 10
    another.sales30 = 10
    assert dummy == another

    another.sales365 = 0
    dummy.update(another)
    assert dummy.sales365 == 0
    dummy.sales365 = 120
    another.sales365 = 120
    assert dummy == another

    another.category_id = "test"
    dummy.update(another)
    assert dummy.category_id == "test"
    dummy.category_id = "dummy_category"
    another.category_id = "dummy_category"
    assert dummy == another

    another.sales_rank = 0
    dummy.update(another)
    assert dummy.sales_rank == 0
    dummy.sales_rank = 1000
    another.sales_rank = 1000
    assert dummy == another


def test_product_amazon_update_none():
    dummy = make_dummy_product_amazon()
    another = make_dummy_product_amazon()

    another.price = None
    dummy.update(another)
    assert dummy.price is not None

    another.fees_fba = None
    dummy.update(another)
    assert dummy.fees_fba is not None

    another.fees_closing = None
    dummy.update(another)
    assert dummy.fees_closing is not None

    another.fees_total = None
    dummy.update(another)
    assert dummy.fees_total is not None

    another.fba_offers = None
    dummy.update(another)
    assert dummy.fba_offers is not None

    another.offers = None
    dummy.update(another)
    assert dummy.offers is not None

    another.has_buy_box = None
    dummy.update(another)
    assert dummy.has_buy_box is not None

    another.review_count = None
    dummy.update(another)
    assert dummy.review_count is not None

    another.rating = None
    dummy.update(another)
    assert dummy.rating is not None

    another.sales30 = None
    dummy.update(another)
    assert dummy.sales30 is not None

    another.sales365 = None
    dummy.update(another)
    assert dummy.sales365 is not None

    another.category_id = None
    dummy.update(another)
    assert dummy.category_id is not None

    another.sales_rank = None
    dummy.update(another)
    assert dummy.sales_rank is not None
