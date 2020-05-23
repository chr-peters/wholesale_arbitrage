import mws
import logging
import time
from wholesale import settings
from wholesale.db.models import ProductAmazon
from decimal import Decimal

products_api = mws.Products(
    settings.AMAZON_MWS["AWS_ACCESS_KEY_ID"],
    settings.AMAZON_MWS["SECRET_KEY"],
    settings.AMAZON_MWS["SELLER_ID"],
    region="DE",
    auth_token=settings.AMAZON_MWS["MWS_AUTH_TOKEN"],
)

marketplace_id_germany = "A1PA6795UKMFR9"

last_matching_product_request_time = 0
last_competitive_pricing_request_time = 0
last_lowest_offer_listings_request_time = 0


def make_api_request(request, retry_count=5, sleep_time=2):
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


def parse_category_id(response_product):
    try:
        return response_product["SalesRankings"]["SalesRank"][0]["ProductCategoryId"][
            "value"
        ]
    except (KeyError, IndexError) as e:
        return None


def parse_sales_rank(response_product):
    try:
        return int(response_product["SalesRankings"]["SalesRank"][0]["Rank"]["value"])
    except (KeyError, IndexError) as e:
        return None


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
        cur_product.category_id = parse_category_id(cur_response_product)
        cur_product.sales_rank = parse_sales_rank(cur_response_product)
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

    response = make_api_request(api_request)
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


def get_price(parsed_response):
    """Returns a dict with a single entry {ASIN: price}"""
    try:
        asin = parsed_response["ASIN"]["value"]
    except KeyError:
        return None
    try:
        listing_price = Decimal(
            parsed_response["Product"]["CompetitivePricing"]["CompetitivePrices"][
                "CompetitivePrice"
            ]["Price"]["ListingPrice"]["Amount"]["value"]
        )
    except KeyError:
        listing_price = 0
    try:
        shipping = Decimal(
            parsed_response["Product"]["CompetitivePricing"]["CompetitivePrices"][
                "CompetitivePrice"
            ]["Price"]["Shipping"]["Amount"]["value"]
        )
    except KeyError:
        shipping = 0
    price = listing_price + shipping
    return {asin: price}


def get_offers(parsed_response):
    """Returns a dict with a single entry {ASIN: offers}"""
    try:
        asin = parsed_response["ASIN"]["value"]
    except KeyError:
        return None
    try:
        offers_by_condition = parsed_response["Product"]["CompetitivePricing"][
            "NumberOfOfferListings"
        ]["OfferListingCount"]
        offer_count = 0
        for cur_offer in offers_by_condition:
            if cur_offer["condition"]["value"] == "New":
                offer_count = int(cur_offer["value"])
                break
    except KeyError:
        return None
    return {asin: offer_count}


def get_lowest_price(parsed_response):
    """
    Returns a dict with a single entry {ASIN: price}. This is not necessarily the
    buy box price. It can be used when there is no buybox.
    """
    try:
        asin = parsed_response["ASIN"]["value"]
    except KeyError:
        return None
    try:
        lowest_offer = parsed_response["Product"]["LowestOfferListings"][
            "LowestOfferListing"
        ]
        if isinstance(lowest_offer, list):
            lowest_offer = lowest_offer[0]
        listing_price = Decimal(
            lowest_offer["Price"]["ListingPrice"]["Amount"]["value"]
        )
        shipping = Decimal(lowest_offer["Price"]["Shipping"]["Amount"]["value"])
        price = listing_price + shipping
    except (KeyError, IndexError):
        return None

    return {asin: price}


def add_competition_details(batch, marketplace_id=marketplace_id_germany):
    global last_lowest_offer_listings_request_time

    asins = [cur_product.asin for cur_product in batch]

    assert len(asins) <= 20  # Maximum of 20 asins is allowed per batch

    def api_request():
        return products_api.get_lowest_offer_listings_for_asin(
            marketplace_id, asins=asins, condition="New"
        )

    elapsed = time.time() - last_lowest_offer_listings_request_time
    if elapsed < 1:
        time.sleep(1 - elapsed)
    response = make_api_request(api_request)
    last_lowest_offer_listings_request_time = time.time()
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

    low_price_data = {}
    for cur_response in response_list:
        lowest_price = get_lowest_price(cur_response)
        if lowest_price is not None:
            low_price_data = {**low_price_data, **lowest_price}

    for cur_product in batch:
        if not cur_product.has_buy_box:
            cur_product.price = low_price_data.get(cur_product.asin, 0)


def add_competition_data(batch, marketplace_id=marketplace_id_germany):
    global last_competitive_pricing_request_time

    asins = [cur_product.asin for cur_product in batch]

    assert len(asins) <= 20  # Maximum of 20 asins is allowed per batch

    def api_request():
        return products_api.get_competitive_pricing_for_asin(marketplace_id, asins)

    elapsed = time.time() - last_competitive_pricing_request_time
    if elapsed < 1:
        time.sleep(1 - elapsed)
    response = make_api_request(api_request)
    last_competitive_pricing_request_time = time.time()
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

    price_data = {}
    offers_data = {}
    for cur_response in response_list:
        if not check_status(cur_response):
            continue
        cur_price_data = get_price(cur_response)
        if cur_price_data is not None:
            price_data = {**price_data, **cur_price_data}
        cur_offers_data = get_offers(cur_response)
        if cur_offers_data is not None:
            offers_data = {**offers_data, **cur_offers_data}

    for cur_product in batch:
        cur_product.price = price_data.get(cur_product.asin)
        if not cur_product.price == 0:
            cur_product.has_buy_box = True
        cur_product.offers = offers_data.get(cur_product.asin, 0)

    add_competition_details(batch, marketplace_id)
