from pathlib import PurePath
import pandas as pd
import requests
from io import StringIO
from wholesale.db.models import ProductWholesale
from wholesale.db import Session
from tqdm import tqdm
import math
from decimal import Decimal

shop_name = "berk.de"

catalog_file_name = "Berk_Kat_2020_EAN_Preise.xlsx"
catalog_file_path = (
    PurePath(__file__).parent.joinpath("./product_catalog").joinpath(catalog_file_name)
)
availability_url = "http://downloads.berk.de/csv/lager_csv_relativ.csv"


def get_availability_csv_string():
    res = requests.get(availability_url)
    res.raise_for_status()
    return res.text


def get_availability_dataframe():
    csv_string = get_availability_csv_string()
    csv_file = StringIO(csv_string)
    df = pd.read_csv(
        csv_file,
        sep=";",
        names=["Artikelnummer", "EANNummer", "Bestand"],
        usecols=["EANNummer", "Bestand"],
        dtype={"EANNummer": str},
        index_col=False,
    )
    csv_file.close()
    return df


def get_product_catalog_dataframe():
    df = pd.read_excel(catalog_file_path, dtype={"EANNummer": str}, encoding="utf-8")
    df.rename(columns={"Preis[VE]": "Preis"}, inplace=True)
    df = df[df["EANNummer"].notnull()]
    return df


def get_product_dataframe():
    availability_dataframe = get_availability_dataframe()
    product_catalog_dataframe = get_product_catalog_dataframe()
    df = pd.merge(
        product_catalog_dataframe,
        availability_dataframe,
        on="EANNummer",
        how="left",
        sort=False,
    )
    return df


def parse_product_dataframe(df):
    for cur_row in df.itertuples():
        if not math.isnan(cur_row.Bestand) and math.isclose(cur_row.Bestand, 0):
            continue
        yield ProductWholesale(
            shop_name=shop_name,
            name=cur_row.Bezeichnung1,
            ean=cur_row.EANNummer,
            price_net=Decimal(cur_row.Preis),
            age_restriction=0,
        )


def update_database():
    df = get_product_dataframe()
    total = sum([1 for cur_product in parse_product_dataframe(df)])
    session = Session()
    for cur_product in tqdm(parse_product_dataframe(df), total=total):
        old_product = (
            session.query(ProductWholesale)
            .filter_by(shop_name=shop_name, ean=cur_product.ean)
            .first()
        )
        if old_product is None:
            session.add(cur_product)
        elif cur_product != old_product:
            old_product.name = cur_product.name
            old_product.price_net = cur_product.price_net
    session.commit()
    session.close()


if __name__ == "__main__":
    update_database()
