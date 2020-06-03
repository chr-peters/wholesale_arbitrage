from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Numeric, TIMESTAMP, Boolean
from sqlalchemy.sql import func
from wholesale.db import engine

Base = declarative_base()


class ProductWholesale(Base):
    __tablename__ = "products_wholesale"

    id = Column(Integer, primary_key=True)
    shop_name = Column(String(length=100), nullable=False)
    name = Column(String(length=500), nullable=False)
    ean = Column(String(length=20), nullable=False)
    price_net = Column(Numeric(precision=8, scale=2), nullable=False)
    age_restriction = Column(Integer, nullable=False, default=0)
    timestamp_created = Column(
        TIMESTAMP, server_default=func.current_timestamp(), nullable=False
    )
    timestamp_updated = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        nullable=False,
    )

    def update(self, other):
        if other.name is not None:
            self.name = other.name
        if other.price_net is not None:
            self.price_net = other.price_net
        if other.age_restriction is not None:
            self.age_restriction = other.age_restriction

    def __eq__(self, other):
        if not self.shop_name == other.shop_name:
            return False
        if not self.name == other.name:
            return False
        if not self.ean == other.ean:
            return False
        if not self.price_net == other.price_net:  # Decimal check is ok
            return False
        if not self.age_restriction == other.age_restriction:
            return False
        return True

    def __repr__(self):
        return (
            f"ProductWholesale("
            f"id={self.id}, "
            f"shop_name='{self.shop_name}', "
            f"name='{self.name}', "
            f"ean='{self.ean}', "
            f"price_net={self.price_net}, "
            f"age_restriction={self.age_restriction}, "
            f"timestamp_created={self.timestamp_created}, "
            f"timestamp_updated={self.timestamp_updated}"
            f")"
        )


class ProductWholesaleItem(ProductWholesale, dict):
    """This is to be used in conjunction with scrapy."""


class ProductAmazon(Base):
    __tablename__ = "products_amazon"

    id = Column(Integer, primary_key=True)
    ean = Column(String(length=20), nullable=False)
    asin = Column(String(length=20), nullable=False)
    price = Column(Numeric(precision=8, scale=2))
    fees = Column(Numeric(precision=8, scale=2))
    fba_offers = Column(Integer)
    offers = Column(Integer)
    has_buy_box = Column(Boolean, default=False)
    review_count = Column(Integer)
    rating = Column(Numeric(precision=3, scale=2))
    sales30 = Column(Integer)
    sales365 = Column(Integer)
    category_id = Column(String(length=200))
    sales_rank = Column(Integer)
    timestamp_created = Column(
        TIMESTAMP, server_default=func.current_timestamp(), nullable=False
    )
    timestamp_updated = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        nullable=False,
    )

    def update(self, other):
        if other.price is not None:
            self.price = other.price
        if other.fees is not None:
            self.fees = other.fees
        if other.fba_offers is not None:
            self.fba_offers = other.fba_offers
        if other.offers is not None:
            self.offers = other.offers
        if other.has_buy_box is not None:
            self.has_buy_box = other.has_buy_box
        if other.review_count is not None:
            self.review_count = other.review_count
        if other.rating is not None:
            self.rating = other.rating
        if other.sales30 is not None:
            self.sales30 = other.sales30
        if other.sales365 is not None:
            self.sales365 = other.sales365
        if other.category_id is not None:
            self.category_id = other.category_id
        if other.sales_rank is not None:
            self.sales_rank = other.sales_rank

    def __eq__(self, other):
        if not self.ean == other.ean:
            return False
        if not self.asin == other.asin:
            return False
        if not self.price == other.price:  # Decimal == check is ok
            return False
        if not self.fees == other.fees:
            return False
        if not self.fba_offers == other.fba_offers:
            return False
        if not self.offers == other.offers:
            return False
        if not self.has_buy_box == other.has_buy_box:
            return False
        if not self.review_count == other.review_count:
            return False
        if not self.rating == other.rating:
            return False
        if not self.sales30 == other.sales30:
            return False
        if not self.sales365 == other.sales365:
            return False
        if not self.category_id == other.category_id:
            return False
        if not self.sales_rank == other.sales_rank:
            return False
        return True

    def __repr__(self):
        return (
            f"ProductAmazon("
            f"id={self.id}, "
            f"ean='{self.ean}', "
            f"asin='{self.asin}', "
            f"price={self.price}, "
            f"fees={self.fees}, "
            f"fba_offers={self.fba_offers}, ",
            f"offers={self.offers}, ",
            f"has_buy_box={self.has_buy_box}, ",
            f"category_id='{self.category_id}', "
            f"salesrank={self.sales_rank}, "
            f"timestamp_created={self.timestamp_created}, "
            f"timestamp_updated={self.timestamp_updated})",
        )


Base.metadata.create_all(engine)
