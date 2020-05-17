import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup


class GrossElectronic:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.request_session = requests.Session()
        self.user_agent = UserAgent().random
        self.login_url = "https://www.gross-electronic.de/"

    def get_login_html(self):
        """Returns a dictionary of all the prepopulated fields in the login form."""
        res = self.request_session.get(
            self.login_url, headers={"User-Agent": self.user_agent}
        )

        if not res.ok:
            raise Exception(
                f"Could not connect to url {self.login_url}. "
                f"Status code: {res.status_code}, reason: {res.reason}"
            )

        return res.text

    def get_login_form_data(self, login_html):
        pass

    def get_csv(self):
        pass
