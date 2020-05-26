import pandas as pd
from wholesale.db import Session
from wholesale.db.models import ProductAmazon, ProductWholesale


def get_raw_data_from_db():
    session = Session()

    query = session.query(
        ProductWholesale.shop_name,
        ProductWholesale.name,
        ProductWholesale.price_net.label("price_shop"),
        ProductWholesale.age_restriction,
        ProductAmazon.ean,
        ProductAmazon.asin,
        ProductAmazon.price.label("price_amazon"),
        ProductAmazon.fees,
        ProductAmazon.fba_offers,
        ProductAmazon.offers,
        ProductAmazon.has_buy_box,
        ProductAmazon.category_id,
        ProductAmazon.sales_rank,
        ProductAmazon.timestamp_updated.label("amazon_updated"),
        ProductWholesale.timestamp_updated.label("wholesale_updated"),
    ).join(ProductAmazon, ProductWholesale.ean == ProductAmazon.ean)
    df = pd.read_sql(query.statement, query.session.bind)

    session.close()

    return df


def estimate_fees(df):
    fba_de_fee = 0.5
    adult_check_fee = 5
    default_shipping = 2
    default_percent = 0.15
    df["fees"] = df["fees"].where(
        ~df["fees"].isna(), df["price_amazon"] * default_percent + default_shipping,
    )
    df["fees"] = df["fees"].where(
        df["age_restriction"] < 18, df["fees"] + adult_check_fee / 1.19
    )
    df["fees"] = df["fees"] + fba_de_fee


def add_taxes(df):
    df["price_shop"] = df["price_shop"] * 1.19
    df["fees"] = df["fees"] * 1.19


def add_profit(df):
    df["profit"] = df["price_amazon"] - df["fees"] - df["price_shop"]


def add_roi(df):
    df["roi"] = df["profit"] / df["price_shop"]


def add_margin(df):
    df["margin"] = df["profit"] / df["price_amazon"]


def add_last_updated(df):
    df["last_updated"] = df[["amazon_updated", "wholesale_updated"]].max(axis=1)


def clean(df):
    df = df[
        [
            "shop_name",
            "name",
            "ean",
            "asin",
            "age_restriction",
            "price_shop",
            "price_amazon",
            "fees",
            "profit",
            "roi",
            "margin",
            "offers",
            "fba_offers",
            "has_buy_box",
            "sales_rank",
            "category_id",
            "last_updated",
        ]
    ]
    return df


def get_data():
    data = get_raw_data_from_db()
    estimate_fees(data)
    add_taxes(data)
    add_profit(data)
    add_roi(data)
    add_margin(data)
    add_last_updated(data)
    data = clean(data)
    return data
