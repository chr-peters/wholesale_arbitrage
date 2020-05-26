import requests
from urllib.parse import urljoin
from wholesale import settings
import json
import time
import math
import logging
from wholesale.utils import retry_request


class KeepaAPI:

    base_url = "https://api.keepa.com/"
    endpoints = {
        "product_request": urljoin(base_url, "product/"),
        "token": urljoin(base_url, "token/"),
    }

    def __init__(self, access_key):
        self.access_key = access_key
        self.tokens_left = 0
        self.refill_rate = 0
        self.refill_in_seconds = 0
        self.last_request_time = 0

        self.update_token_status()

    def update_token_status(self):
        params = {"key": self.access_key}
        self.make_request(
            endpoint=KeepaAPI.endpoints["token"], params=params, min_tokens=0
        )

    def wait_for_refill(self, tokens_needed):
        refills_needed = math.ceil(
            (tokens_needed - self.tokens_left) / self.refill_rate
        )
        sleep_time = max(
            self.refill_in_seconds
            + self.last_request_time
            - time.time()
            + (refills_needed - 1) * 60,
            0,
        )
        time.sleep(sleep_time)

    def make_request(self, endpoint, params, min_tokens):
        if self.tokens_left < min_tokens:
            self.wait_for_refill(min_tokens)

        def request():
            return requests.get(endpoint, params=params)

        response = retry_request(request)
        self.last_request_time = time.time()

        if not response.ok:
            raise Exception(
                f"Failed request to keepa API. Status-code: {response.status_code}, "
                f"Reason: {response.reason}.\n"
                f"Url: {response.url}\n"
                f"Dumping response text:\n{response.text}"
            )

        response_dict = json.loads(response.text)
        self.tokens_left = response_dict["tokensLeft"]
        self.refill_in_seconds = response_dict["refillIn"] / 1000
        self.refill_rate = response_dict["refillRate"]

        return response_dict

    def get_rating_and_sales_info(self, asin, domain_id=3):
        params = {
            "key": self.access_key,
            "domain": domain_id,
            "asin": asin,
            "stats": 365,
            "rating": 1,
            "update": 24,
        }
        res = self.make_request(
            endpoint=KeepaAPI.endpoints["product_request"], params=params, min_tokens=3
        )

        if "products" not in res.keys():
            logging.error(f"No data available for ASIN {asin}")
            return None

        rating_list = res["products"][0]["csv"][16]
        rating = None
        if rating_list is not None:
            rating = rating_list[-1] / 10

        review_count_list = res["products"][0]["csv"][17]
        review_count = 0
        if review_count_list is not None:
            review_count = review_count_list[-1]

        result = {
            "review_count": review_count,
            "rating": rating,
            "sales30": res["products"][0]["stats"]["salesRankDrops30"],
            "sales365": res["products"][0]["stats"]["salesRankDrops365"],
        }
        return result


_instance = KeepaAPI(settings.KEEPA_ACCESS_KEY)
get_rating_and_sales_info = _instance.get_rating_and_sales_info


if __name__ == "__main__":
    print(get_rating_and_sales_info("B07Y1YMFKP"))
    print(get_rating_and_sales_info("B0065ILAMI"))
    print(get_rating_and_sales_info("B002W131GU"))
    print(get_rating_and_sales_info("B002W131AAdf"))
