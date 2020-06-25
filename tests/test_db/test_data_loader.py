import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tests.settings import DATABASE_MYSQL_TEST
from wholesale import db
from wholesale.db import models
from wholesale.db import data_loader
from tests.utils import make_dummy_product_wholesale, make_dummy_product_amazon


@pytest.fixture
def test_engine():
    test_connection_url = (
        f"mysql+pymysql://{DATABASE_MYSQL_TEST['USER']}:"
        f"{DATABASE_MYSQL_TEST['PASSWORD']}@{DATABASE_MYSQL_TEST['HOST']}/"
        f"{DATABASE_MYSQL_TEST['DBNAME']}"
    )
    test_engine = create_engine(test_connection_url)
    models.Base.metadata.create_all(test_engine)
    return test_engine


@pytest.fixture
def test_session_class(test_engine):
    return sessionmaker(bind=test_engine)


@pytest.fixture
def test_session(test_session_class):
    session = test_session_class()
    yield session
    session.rollback()
    session.query(models.ProductAmazon).delete()
    session.query(models.ProductWholesale).delete()
    session.commit()
    session.close()


def test_db_empty(test_session):
    session = test_session
    wholesale_products = session.query(models.ProductWholesale).all()
    amazon_products = session.query(models.ProductAmazon).all()

    assert len(wholesale_products) == 0
    assert len(amazon_products) == 0


def test_get_raw_data_empty(test_session):
    df = data_loader.get_raw_data_from_db(test_session)
    assert len(df) == 0


def test_get_raw_data_columns(test_session):
    df = data_loader.get_raw_data_from_db(test_session)
    assert df.columns.tolist() == [
        "shop_name",
        "name",
        "price_shop",
        "age_restriction",
        "is_available",
        "ean",
        "asin",
        "price_amazon",
        "fees_fba_net",
        "fees_closing_net",
        "fees_total",
        "fba_offers",
        "offers",
        "has_buy_box",
        "review_count",
        "rating",
        "sales30",
        "sales365",
        "category_id",
        "sales_rank",
        "amazon_updated",
        "wholesale_updated",
    ]


def test_get_raw_data_single_row(test_session):
    dummy_wholesale = make_dummy_product_wholesale()
    dummy_amazon = make_dummy_product_amazon()
    dummy_wholesale.ean = "1234"
    dummy_amazon.ean = "1234"

    test_session.add(dummy_wholesale)
    test_session.add(dummy_amazon)
    test_session.commit()

    df = data_loader.get_raw_data_from_db(test_session)

    assert len(df) == 1
    row = df.iloc[0]
    assert row["shop_name"] == dummy_wholesale.shop_name
    assert row["name"] == dummy_wholesale.name
    assert row["price_shop"] == dummy_wholesale.price_net
    assert row["age_restriction"] == dummy_wholesale.age_restriction
    assert row["is_available"] == dummy_wholesale.is_available
    assert row["ean"] == dummy_wholesale.ean
    assert row["ean"] == dummy_amazon.ean
    assert row["asin"] == dummy_amazon.asin
    assert row["price_amazon"] == dummy_amazon.price
    assert row["fees_fba_net"] == dummy_amazon.fees_fba
    assert row["fees_closing_net"] == dummy_amazon.fees_closing
    assert row["fees_total"] == dummy_amazon.fees_total
    assert row["fba_offers"] == dummy_amazon.fba_offers
    assert row["offers"] == dummy_amazon.offers
    assert row["has_buy_box"] == dummy_amazon.has_buy_box
    assert row["review_count"] == dummy_amazon.review_count
    assert row["rating"] == dummy_amazon.rating
    assert row["sales30"] == dummy_amazon.sales30
    assert row["sales365"] == dummy_amazon.sales365
    assert row["category_id"] == dummy_amazon.category_id
    assert row["sales_rank"] == dummy_amazon.sales_rank
