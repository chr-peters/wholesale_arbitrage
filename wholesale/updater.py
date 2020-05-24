from wholesale.shops import gross_electronic
from wholesale.amazon import amazon_db
from wholesale.ui import data_display
import logging


def update_gross_electronic():
    gross_electronic.update_database()
    logging.info("Updating Amazon db")
    amazon_db.update_database(gross_electronic.shop_name)
    logging.info("Done.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    update_gross_electronic()
    data_display.display_data()