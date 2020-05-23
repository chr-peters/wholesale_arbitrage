import mws
import logging
import time
from wholesale import settings
from wholesale.db.models import ProductAmazon

products_api = mws.Products(
    settings.AMAZON_MWS["AWS_ACCESS_KEY_ID"],
    settings.AMAZON_MWS["SECRET_KEY"],
    settings.AMAZON_MWS["SELLER_ID"],
    region="DE",
    auth_token=settings.AMAZON_MWS["MWS_AUTH_TOKEN"],
)

marketplace_id_germany = "A1PA6795UKMFR9"

last_matching_product_request_time = 0


def make_api_request(request, retry_count, sleep_time=2):
    success = False
    last_request_time = 0
    while not success:
        try:
            elapsed = time.time() - last_request_time
            if elapsed < sleep_time:
                time.sleep(sleep_time - elapsed)
            response = request()
            last_request_time = time.time()
            success = True
        except Exception as e:
            if retry_count > 1:
                logging.error("An exception ocured. Trying again.")
                logging.error(e)
                retry_count = retry_count - 1
                time.sleep(sleep_time)
            else:
                logging.critical("Maximum number of retries reached.")
                raise e
    return response


def check_status(parsed_response):
    if parsed_response["status"]["value"] == "Success":
        return True
    logging.error(parsed_response["Error"]["Message"]["value"])
    return False


def parse_ean(parsed_response):
    # make sure it's an EAN before parsing it
    id_type = parsed_response["IdType"]["value"]
    if not id_type == "EAN":
        raise Exception(f"Tried parsing EAN despite IdType being {id_type}")
    ean = parsed_response["Id"]["value"]
    return ean


def parse_asin(response_product):
    return response_product["Identifiers"]["MarketplaceASIN"]["ASIN"]["value"]


def is_bundle(response_product):
    if (
        response_product["AttributeSets"]["ItemAttributes"]["Binding"]["value"]
        == "Product Bundle"
    ):
        return True
    return False


def get_response_products_list(parsed_response):
    result = []
    if isinstance(parsed_response["Products"]["Product"], list):
        result.extend(parsed_response["Products"]["Product"])
    else:
        result.append(parsed_response["Products"]["Product"])
    return result


def parse_base_data(parsed_response):
    if not check_status(parsed_response):
        return []

    ean = parse_ean(parsed_response)

    result = []
    for cur_response_product in get_response_products_list(parsed_response):
        if is_bundle(cur_response_product):
            continue

        cur_product = ProductAmazon()
        cur_product.ean = ean
        cur_product.asin = parse_asin(cur_response_product)
        result.append(cur_product)

    return result


def get_base_data(batch, marketplace_id=marketplace_id_germany):
    """
    Takes a batch of ProductWholesale objects as a list and returns the
    corresponding ProductAmazon objects by making a request to the mws api.
    The result will only contain the base data and no information about the price
    and the fees.
    """
    global last_matching_product_request_time

    ean_codes = [cur_product.ean for cur_product in batch]

    def api_request():
        return products_api.get_matching_product_for_id(
            marketplace_id, type_="EAN", ids=ean_codes
        )

    elapsed = time.time() - last_matching_product_request_time
    if elapsed < 1:  # wait at least 1 seconds between requests
        time.sleep(1 - elapsed)

    response = make_api_request(api_request, retry_count=5)
    last_matching_product_request_time = time.time()
    if not response.response.ok:
        raise Exception(
            f"Could not make request to MWS API. "
            f"Status code: {response.response.status_code}, "
            f"Reason: {response.response.reason}."
        )

    response_list = []
    if isinstance(response.parsed, list):
        response_list.extend(response.parsed)
    else:
        response_list.append(response.parsed)

    result_list = []
    for cur_response in response_list:
        cur_result = parse_base_data(cur_response)
        result_list.extend(cur_result)

    return result_list
