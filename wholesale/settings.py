import os

DATABASE_MYSQL = {
    "HOST": os.environ["WHOLESALE_MYSQL_HOST"],
    "PORT": os.environ["WHOLESALE_MYSQL_PORT"],
    "USER": os.environ["WHOLESALE_MYSQL_USER"],
    "PASSWORD": os.environ["WHOLESALE_MYSQL_PASSWORD"],
    "DBNAME": os.environ["WHOLESALE_MYSQL_DBNAME"],
}

AMAZON_MWS = {
    "AWS_ACCESS_KEY_ID": os.environ["AWS_ACCESS_KEY_ID"],
    "SECRET_KEY": os.environ["AMAZON_SECRET_KEY"],
    "SELLER_ID": os.environ["AMAZON_SELLER_ID"],
    "MWS_AUTH_TOKEN": os.environ["MWS_AUTH_TOKEN"],
}

GROSS_ELECTRONIC = {
    "USER": os.environ["WHOLESALE_GROSS_ELECTRONIC_USER"],
    "PASSWORD": os.environ["WHOLESALE_GROSS_ELECTRONIC_PASSWORD"],
}

NLG_SHOP = {
    "USER": os.environ["WHOLESALE_NLG_SHOP_USER"],
    "PASSWORD": os.environ["WHOLESALE_NLG_SHOP_PASSWORD"],
}

VITREX = {
    "USER": os.environ["WHOLESALE_VITREX_USER"],
    "PASSWORD": os.environ["WHOLESALE_VITREX_PASSWORD"],
}

KEEPA_ACCESS_KEY = os.environ["KEEPA_ACCESS_KEY"]
