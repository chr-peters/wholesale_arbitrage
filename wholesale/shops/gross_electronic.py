import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re


base_url = "https://www.gross-electronic.de/"


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


class GrossElectronic:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.request_session = requests.Session()
        self.default_headers = {"User-Agent": UserAgent().random}

    def get_login_html(self):
        """Returns the html code of the login page."""
        res = self.request_session.get(base_url, headers=self.default_headers)

        if not res.ok:
            raise Exception(
                f"Could not connect to url {base_url}. "
                f"Status code: {res.status_code}, reason: {res.reason}"
            )

        return res.text

    def login(self, login_html):
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
                f"Could not login at url {url}. "
                f"Status code: {res.status_code}, reason: {res.reason}"
            )

        # The website performs a client side redirect using Javascript.
        # Simulate this by parsing the target url using a regular expression.

        url_finder = re.compile(".*'(?P<url>.*)'.*")
        match = re.match(url_finder, res.text)
        target_url = urljoin(base_url, match.group("url"))

        res = self.request_session.get(target_url, headers=self.default_headers)

        if not res.ok:
            raise Exception(
                f"Error after login redirect to {url}. "
                f"Status code: {res.status_code}, reason: {res.reason}"
            )

        return res.text
