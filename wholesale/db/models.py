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
    ean = Column(String(length=13), nullable=False)
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

    def __eq__(self, other):
        if not self.shopname == other.shop_name:
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
            f"name='{self.name}, "
            f"ean={self.ean}', "
            f"price_net={self.price_net}, "
            f"age_restriction={self.age_restriction}, "
            f"timestamp_created={self.timestamp_created}, "
            f"timestamp_updated={self.timestamp_updated}"
            f")"
        )


class ProductAmazon(Base):
    __tablename__ = "products_amazon"

    id = Column(Integer, primary_key=True)
    ean = Column(String(length=13), nullable=False)
    asin = Column(String(length=20), nullable=False)
    price = Column(Numeric(precision=8, scale=2))
    fees = Column(Numeric(precision=8, scale=2))
    fba_offers = Column(Integer)
    offers = Column(Integer)
    has_buy_box = Column(Boolean, default=False)
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
