from pathlib import PurePath
import pandas as pd
import requests
from io import StringIO

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


def update_database():
    pass
