import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import time
import io
import csv
from decimal import Decimal
from ..db import Session
from ..db.models import ProductWholesale
from .. import settings


base_url = "https://www.gross-electronic.de/"
shop_name = "gross-electronic.de"


def get_hidden_login_field_data(login_html):
    """Returns a dictionary of all the hidden fields in the login form."""

    bs = BeautifulSoup(login_html, "html.parser")
    login_form = bs.find("form", attrs={"name": "formular_login"})
    hidden_fields = login_form.find_all("input", type="hidden")
    result = {}
    for cur_hidden_field in hidden_fields:
        result[cur_hidden_field["name"]] = cur_hidden_field["value"]
    return result


def get_login_action_url(login_html):
    """Returns the action url from the login form."""

    bs = BeautifulSoup(login_html, "html.parser")
    login_form = bs.find("form", attrs={"name": "formular_login"})
    return urljoin(base_url, login_form["action"])


def get_login_redirect_url(login_form_response):
    """
    After login, a client side redirect is performed using javascript.
    This function parses the Javascript to get the url to redirect to.
    """

    url_finder = re.compile(".*'(?P<url>.*)'.*")
    match = re.match(url_finder, login_form_response)
    redirect_url = urljoin(base_url, match.group("url"))
    return redirect_url


def get_download_area_url(after_login_html):
    bs = BeautifulSoup(after_login_html, "html.parser")
    csv_link = bs.find("a", string="Downloadbereich CSV")
    csv_url = csv_link["href"]
    return urljoin(base_url, csv_url)


def get_export_area_url(download_area_html):
    bs = BeautifulSoup(download_area_html, "html.parser")
    export_link = bs.find(
        "a", string="Artikelexport/Datenbank für Ihren Webshop als txt oder csv Datei"
    )
    export_url = export_link["href"]
    return urljoin(base_url, export_url)


def get_export_url(export_area_html):
    bs = BeautifulSoup(export_area_html, "html.parser")
    export_frame = bs.find("frame", attrs={"name": "export"})
    export_url = export_frame["src"]
    return urljoin(urljoin(base_url, "/exportfile/"), export_url)


def get_csv_url(export_html):
    bs = BeautifulSoup(export_html, "html.parser")

    def csv_link_identifier(tag):
        if not tag.name == "a":
            return False
        if (
            "Exportdatei .CSV im Excel-Format downloaden (bitte hier klicken)"
            in tag.strings
        ):
            return True
        return False

    csv_link = bs.find(csv_link_identifier)
    csv_url = csv_link["href"]
    return urljoin(urljoin(base_url, "/exportfile/"), csv_url)


class GrossElectronic:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.request_session = requests.Session()
        self.default_headers = {"User-Agent": UserAgent().firefox}

    def send_login_form(self, login_html):
        """
        Sends the login form. Returns the response text which contains a Javascript
        client side redirect.
        """

        hidden_field_data = get_hidden_login_field_data(login_html)
        request_body = {
            **hidden_field_data,
            "userBez": self.username,
            "userPasswort": self.password,
        }
        url = get_login_action_url(login_html)

        res = self.request_session.post(
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
        Returns the body of the response.
        """

        res = self.request_session.get(url, headers=self.default_headers)

        if not res.ok:
            raise Exception(
                f"Error while getting html for url {url}. "
                f"Status code: {res.status_code}, reason: {res.reason}"
            )

        return res.text

    def get_csv_string(self):
        login_html = self.get_response_text(base_url)
        time.sleep(1)

        login_form_response = self.send_login_form(login_html)
        redirect_url = get_login_redirect_url(login_form_response)
        time.sleep(1)

        after_login_html = self.get_response_text(redirect_url)
        download_area_url = get_download_area_url(after_login_html)
        time.sleep(1)

        download_area_html = self.get_response_text(download_area_url)
        export_area_url = get_export_area_url(download_area_html)
        time.sleep(1)

        export_area_html = self.get_response_text(export_area_url)
        export_url = get_export_url(export_area_html)
        time.sleep(1)

        export_html = self.get_response_text(export_url)
        csv_url = get_csv_url(export_html)
        time.sleep(1)

        csv_string = self.get_response_text(csv_url)

        return csv_string


def parse_csv(csv_file):
    reader = csv.DictReader(csv_file, delimiter=";")
    for cur_record in reader:
        age_restriction = 0
        try:
            age_restriction = int(cur_record["USK/FSK"])
        except ValueError:
            pass
        yield ProductWholesale(
            shop_name=shop_name,
            name=cur_record["Bezeichnung"],
            ean=cur_record["EAN"],
            price_net=Decimal(cur_record["Ihr Preis"]),
            age_restriction=age_restriction,
        )


def update_database():
    gross = GrossElectronic(
        username=settings.GROSS_ELECTRONIC["USER"],
        password=settings.GROSS_ELECTRONIC["PASSWORD"],
    )
    csv_string = gross.get_csv_string()
    csv_file = io.StringIO(csv_string)

    session = Session()
    for cur_product in parse_csv(csv_file):
        # TODO: Update if exists
        session.add(cur_product)
    session.commit()
    session.close()
