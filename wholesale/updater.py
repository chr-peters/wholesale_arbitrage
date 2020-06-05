from wholesale.shops import gross_electronic, nlgshop, vitrex, berk, saraswati
from wholesale.amazon import amazon_db
from wholesale.ui import data_display
from wholesale import keepa
import logging


def update_shop(shop):
    shop.update_database()
    logging.info("Updating Amazon db")
    amazon_db.update_database(shop.shop_name)
    logging.info("Updating un-updated profitable products keepa data")
    keepa.update_profitable_unupdated_products(shop.shop_name)
    logging.info("Done.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # update_shop(gross_electronic)
    update_shop(berk)
    data_display.display_data()
