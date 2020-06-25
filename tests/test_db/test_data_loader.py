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
    session.execute(f"drop table {models.ProductWholesale.__tablename__}")
    session.execute(f"drop table {models.ProductAmazon.__tablename__}")
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


def test_calculations(test_session):
    dummy_wholesale = models.ProductWholesale(
        shop_name="dummy_shop",
        name="dummy_product",
        ean="abc",
        is_available=True,
        price_net=10,
        age_restriction=18,
    )
    dummy_amazon = models.ProductAmazon(
        ean="abc",
        asin="abc123",
        price=30,
        fees_fba=1,
        fees_closing=1,
        fees_total=6.5,
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

    test_session.add(dummy_wholesale)
    test_session.add(dummy_amazon)
    test_session.commit()

    df = data_loader.get_data(test_session)
    row = df.iloc[0]

    assert row["shop_name"] == "dummy_shop"
    assert row["name"] == "dummy_product"
    assert row["ean"] == "abc"
    assert row["asin"] == "abc123"
    assert row["is_available"] == True
    assert row["age_restriction"] == 18
    assert row["price_shop"] == 10 * (1 + data_loader.vat_tax)
    assert row["price_amazon"] == 30
    break_even = (
        (1 + data_loader.vat_tax)
        / (1 - 0.15 * (1 + data_loader.vat_tax))
        * (10 + 1 + 1 + data_loader.fba_de_fee + data_loader.adult_check_fee)
    )
    assert row["break_even"] == break_even
    assert round(row["safety_percent"], 6) == round(1 - break_even / 30, 6)
    profit = (
        30
        - 30 * 0.15 * (1 + data_loader.vat_tax)
        - 1 * (1 + data_loader.vat_tax)
        - 1 * (1 + data_loader.vat_tax)
        - data_loader.fba_de_fee * (1 + data_loader.vat_tax)
        - data_loader.adult_check_fee * (1 + data_loader.vat_tax)
        - 10 * (1 + data_loader.vat_tax)
    )
    assert round(row["profit"], 6) == round(profit, 6)
    assert round(row["roi"], 6) == round(profit / (10 * (1 + data_loader.vat_tax)), 6)
    assert round(row["margin"], 6) == round(profit / 30, 6)
    assert row["sales30"] == 10
    assert row["sales365"] == 120
    assert row["offers"] == 2
    assert row["fba_offers"] == 1
    assert row["has_buy_box"] == True
    assert row["review_count"] == 10
    assert row["rating"] == 5
    assert row["fees_percentage"] == 0.15
    assert row["fees_fba_net"] == 1
    assert row["fees_closing_net"] == 1
    fees_total = (
        30 * 0.15 + 1 + 1 + data_loader.adult_check_fee + data_loader.fba_de_fee
    ) * (1 + data_loader.vat_tax)
    assert round(row["fees_total"], 6) == round(fees_total, 6)
    assert row["sales_rank"] == 1000
    assert row["category_id"] == "dummy_category"
