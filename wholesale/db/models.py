from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Numeric, TIMESTAMP
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
            f"shop_name={self.shop_name}, "
            f"name={self.name}, ean={self.ean}, "
            f"price_net={self.price_net}, "
            f"age_restriction={self.age_restriction}, "
            f"timestamp_created={self.timestamp_created}, "
            f"timestamp_updated={self.timestamp_updated}"
            f")"
        )


Base.metadata.create_all(engine)
