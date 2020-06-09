import requests
from fake_useragent import UserAgent
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import logging
import time
from io import StringIO
import csv
from tqdm import tqdm
from wholesale.db.models import ProductWholesale
from wholesale.db import Session
from decimal import Decimal
from wholesale import settings
from wholesale.utils import retry_request
from wholesale.db import data_loader


shop_name = "vitrex.de"
base_url = "https://www.vitrex-shop.de/"
login_url = urljoin(base_url, "de/login__10/")
csv_download_url = urljoin(base_url, "ajax.php?dl_link=1")

last_availability_request_time = 0


def get_hidden_login_field_data(login_html):
    """Returns a dictionary of all the hidden fields in the login form."""

    bs = BeautifulSoup(login_html, "html.parser")
    login_form = bs.find("form", attrs={"class": "login-form"})

    if login_form is None:
        logging.critical("Could not find login form in login html. HTML-Dump:")
        logging.critical(bs.prettify())
        raise Exception("Could not find login form.")

    hidden_fields = login_form.find_all("input", type="hidden")
    result = {}
    for cur_hidden_field in hidden_fields:
        result[cur_hidden_field["name"]] = cur_hidden_field["value"]
    return result


def is_login_successful(after_login_html):
    """Tests if login was successful by finding the logout button."""
    bs = BeautifulSoup(after_login_html, "html.parser")
    logout_link = bs.find("a", title="Ausloggen")
    if logout_link is None:
        return False
    return True


def is_available(ean):
    global last_availability_request_time

    params = {"quicksearch": ean, "search_button": 1}
    headers = {"User-Agent": UserAgent().firefox}
    url = "https://www.vitrex-shop.de/de/erweiterte-suche__13/"

    time_diff = time.time() - last_availability_request_time
    if time_diff < 1:
        time.sleep(1 - time_diff)

    response = requests.get(url, params=params, headers=headers)
    last_availability_request_time = time.time()
    response.raise_for_status()

    bs = BeautifulSoup(response.text, "html.parser")

    ean_div = bs.find("div", string=lambda x: x is not None and x.strip() == ean)
    if ean_div is None:
        return False
    stock_span = ean_div.parent.find("span", attrs={"class": "stock"})
    if stock_span is None:
        logging.warning(f"No stock information found for EAN {ean}")
        return False
    stock_title = stock_span.attrs.get("title")
    if stock_title is None:
        logging.warning(f"No stock title found for EAN {ean}")
        return False

    stock_title = stock_title.strip()
    if stock_title == "geringer Warenbestand":
        return True
    if stock_title == "großer Warenbestand":
        return True
    if stock_title == "vorbestellbar":
        return True
    return False


class Vitrex:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.requests_session = requests.Session()
        self.default_headers = {"User-Agent": UserAgent().firefox}

    def send_login_form(self, login_html):
        """
        Sends the login form. Returns the response text which contains a Javascript
        client side redirect.
        """

        hidden_field_data = get_hidden_login_field_data(login_html)
        request_body = {
            **hidden_field_data,
            "usrLogin": self.username,
            "passLogin": self.password,
        }
        url = login_url

        res = self.requests_session.post(
            url, data=request_body, headers=self.default_headers
        )

        if not res.ok:
            raise Exception(
                f"Could not send login form to {url}. "
                f"Status code: {res.status_code}, reason: {res.reason}"
            )

        return res.text

    def get_response_text(self, url):
        """
        Makes a get request to url using the request_session.
        Returns the body text of the response.
        """

        res = self.requests_session.get(url, headers=self.default_headers)

        if not res.ok:
            raise Exception(
                f"Error while sending GET to url {url}. "
                f"Status code: {res.status_code}, reason: {res.reason}"
            )

        return res.text

    def get_csv_string(self):
        logging.info("Requesting login html")
        login_html = self.get_response_text(login_url)
        logging.info("Done.")
        time.sleep(2)

        logging.info("Logging in")
        after_login_html = self.send_login_form(login_html)
        if not is_login_successful(after_login_html):
            logging.critical("Login not successful! HTML-Dump:")
            bs = BeautifulSoup(after_login_html)
            logging.critical(bs.prettify())
            raise Exception("Login not successful!")
        logging.info("Done.")
        time.sleep(2)

        logging.info("Downloading csv")
        csv_raw_text = self.get_response_text(csv_download_url)
        logging.info("Done.")

        return csv_raw_text


def get_product_count(csv_file):
    reader = csv.DictReader(csv_file, delimiter=";")
    product_count = 0
    try:
        for cur_record in reader:
            if cur_record["USK"] == "indiziert" or cur_record["EAN"].strip() == "":
                continue
            product_count = product_count + 1
    except csv.Error as e:
        if str(e) != "line contains NUL":  # the last line in this .csv is NUL
            raise e
    return product_count


def parse_csv(csv_file):
    reader = csv.DictReader(csv_file, delimiter=";")
    try:
        for cur_record in reader:
            if cur_record["EAN"].strip() == "":
                continue

            if cur_record["USK"] == "indiziert" or cur_record["EAN"].strip() == "":
                continue
            age_restriction = 0
            try:
                age_restriction = int(cur_record["USK"])
            except ValueError:
                pass
            yield ProductWholesale(
                shop_name=shop_name,
                name=cur_record["Titel"],
                ean=cur_record["EAN"],
                price_net=Decimal(cur_record["Preis"].replace(",", ".")),
                age_restriction=age_restriction,
            )
    except csv.Error as e:
        if str(e) != "line contains NUL":  # the last line in this .csv is NUL
            raise e


def update_database():
    vitrex = Vitrex(
        username=settings.VITREX["USER"], password=settings.VITREX["PASSWORD"],
    )
    csv_string = vitrex.get_csv_string()
    csv_file = StringIO(csv_string)
    product_count = get_product_count(csv_file)
    csv_file.close()
    csv_file = StringIO(csv_string)

    logging.info("Started parsing csv")
    session = Session()
    for cur_product in tqdm(parse_csv(csv_file), total=product_count):
        old_product = (
            session.query(ProductWholesale)
            .filter_by(shop_name=shop_name, ean=cur_product.ean)
            .first()
        )
        if old_product is None:
            session.add(cur_product)
            session.commit()
        elif cur_product != old_product:
            old_product.update(cur_product)
            session.commit()
    session.close()
    csv_file.close()
    logging.info("Done.")


def clean_profitable_products():
    df = data_loader.get_data()
    df = df[(df["shop_name"] == shop_name) & (df["profit"] > 0)]
    ean_list = df["ean"]

    session = Session()
    query = session.query(ProductWholesale).filter(ProductWholesale.ean.in_(ean_list))
    for cur_product in tqdm(query, total=query.count()):

        def availability_check_request():
            return is_available(cur_product.ean)

        cur_availability = retry_request(availability_check_request)
        cur_product.is_available = cur_availability
        session.commit()

    session.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    update_database()
    # clean_profitable_products()
