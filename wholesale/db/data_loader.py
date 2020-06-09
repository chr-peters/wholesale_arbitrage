import pandas as pd
from wholesale.db import Session
from wholesale.db.models import ProductAmazon, ProductWholesale

fba_de_fee = 0.5
adult_check_fee = 5
default_shipping = 2
default_percent = 0.15
vat_tax = 0.19


def get_raw_data_from_db():
    session = Session()

    query = session.query(
        ProductWholesale.shop_name,
        ProductWholesale.name,
        ProductWholesale.price_net.label("price_shop"),
        ProductWholesale.age_restriction,
        ProductWholesale.is_available,
        ProductAmazon.ean,
        ProductAmazon.asin,
        ProductAmazon.price.label("price_amazon"),
        ProductAmazon.fees_fba.label("fees_fba_net"),
        ProductAmazon.fees_closing.label("fees_closing_net"),
        ProductAmazon.fees_total,
        ProductAmazon.fba_offers,
        ProductAmazon.offers,
        ProductAmazon.has_buy_box,
        ProductAmazon.review_count,
        ProductAmazon.rating,
        ProductAmazon.sales30,
        ProductAmazon.sales365,
        ProductAmazon.category_id,
        ProductAmazon.sales_rank,
        ProductAmazon.timestamp_updated.label("amazon_updated"),
        ProductWholesale.timestamp_updated.label("wholesale_updated"),
    ).join(ProductAmazon, ProductWholesale.ean == ProductAmazon.ean)
    df = pd.read_sql(query.statement, query.session.bind)

    session.close()

    return df


def estimate_fees(df):
    df["fees_percentage"] = round(
        (df["fees_total"] - df["fees_fba_net"] - df["fees_closing_net"])
        / df["price_amazon"],
        2,
    )
    df["fees_total"] = df["fees_total"].where(
        ~df["fees_total"].isna(),
        df["price_amazon"] * default_percent + default_shipping,
    )
    df["fees_total"] = df["fees_total"].where(
        df["age_restriction"] < 18, df["fees_total"] + adult_check_fee / 1.19
    )
    df["fees_total"] = df["fees_total"] + fba_de_fee


def add_taxes(df):
    df["price_shop"] = df["price_shop"] * 1.19
    df["fees_total"] = df["fees_total"] * 1.19


def add_profit(df):
    df["profit"] = df["price_amazon"] - df["fees_total"] - df["price_shop"]


def add_roi(df):
    df["roi"] = df["profit"] / df["price_shop"]


def add_margin(df):
    df["margin"] = df["profit"] / df["price_amazon"]


def add_last_updated(df):
    df["last_updated"] = df[["amazon_updated", "wholesale_updated"]].max(axis=1)


def add_break_even(df):
    df["age_fee"] = 0
    df["age_fee"].where(
        df["age_restriction"] < 18, adult_check_fee / (1 + vat_tax), inplace=True
    )
    df["break_even"] = (
        (1 + vat_tax)
        / (1 - df["fees_percentage"] * (1 + vat_tax))
        * (
            df["price_shop"] / (1 + vat_tax)
            + df["fees_closing_net"]
            + df["fees_fba_net"]
            + df["age_fee"]
            + fba_de_fee
        )
    )
    df["safety_percent"] = (df["price_amazon"] - df["break_even"]) / df["price_amazon"]


def clean(df):
    df = df[
        [
            "shop_name",
            "name",
            "ean",
            "asin",
            "is_available",
            "age_restriction",
            "price_shop",
            "price_amazon",
            "break_even",
            "safety_percent",
            "fees_percentage",
            "fees_fba_net",
            "fees_closing_net",
            "fees_total",
            "profit",
            "roi",
            "margin",
            "offers",
            "fba_offers",
            "has_buy_box",
            "review_count",
            "rating",
            "sales30",
            "sales365",
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
    add_break_even(data)
    data = clean(data)
    return data
