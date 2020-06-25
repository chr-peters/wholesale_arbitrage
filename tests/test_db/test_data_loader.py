import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tests.settings import DATABASE_MYSQL_TEST
from wholesale import db
from wholesale.db import models
from wholesale.db import data_loader


@pytest.fixture
def test_engine():
    test_connection_url = (
        f"mysql+pymysql://{DATABASE_MYSQL_TEST['USER']}:"
        f"{DATABASE_MYSQL_TEST['PASSWORD']}@{DATABASE_MYSQL_TEST['HOST']}/"
        f"{DATABASE_MYSQL_TEST['DBNAME']}"
    )
    test_engine = create_engine(test_connection_url)
    return test_engine


@pytest.fixture
def test_session_class(test_engine):
    return sessionmaker(bind=test_engine)


@pytest.fixture
def test_session(test_session_class):
    session = test_session_class()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def test_db(monkeypatch, test_engine, test_session_class):
    monkeypatch.setattr(db, "engine", test_engine)
    monkeypatch.setattr(db, "Session", test_session_class)
    monkeypatch.setattr(data_loader, "Session", test_session_class)
    models.Base.metadata.create_all(test_engine)


def test_db_empty(test_session):
    session = test_session
    wholesale_products = session.query(models.ProductWholesale).all()
    amazon_products = session.query(models.ProductAmazon).all()

    assert len(wholesale_products) == 0
    assert len(amazon_products) == 0


def test_get_raw_data_empty(test_db):
    df = data_loader.get_raw_data_from_db()
    assert len(df) == 0


def test_get_raw_data_columns(test_db):
    df = data_loader.get_raw_data_from_db()
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
