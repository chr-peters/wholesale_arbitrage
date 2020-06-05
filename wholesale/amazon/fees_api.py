import requests
from decimal import Decimal
import hmac
import base64
import datetime
from wholesale import settings
from wholesale.db import Session
from wholesale.db.models import ProductAmazon
from bs4 import BeautifulSoup
import logging


class FeesAPI:
    mws_endpoint = "https://mws-eu.amazonservices.com/Products/2011-10-01"

    def __init__(self, aws_access_key_id, secret_key, seller_id, mws_auth_token):
        self.aws_access_key_id = aws_access_key_id
        self.secret_key = secret_key
        self.seller_id = seller_id
        self.mws_auth_token = mws_auth_token

    def get_my_fees_estimate(self, marketplace_id, products):
        assert len(products) > 0
        assert len(products) <= 20

        # this is the basic information that has to be sent with every request
        data_unsorted = {
            "Action": "GetMyFeesEstimate",
            "AWSAccessKeyId": self.aws_access_key_id,
            "MWSAuthToken": self.mws_auth_token,
            "SellerId": self.seller_id,
            "SignatureMethod": "HmacSHA256",
            "SignatureVersion": "2",
            "Timestamp": datetime.datetime.utcnow().isoformat(),
            "Version": "2011-10-01",
        }

        # now append the products to this data
        listindex = 1
        for cur_product in products:
            data_unsorted[
                "FeesEstimateRequestList.FeesEstimateRequest."
                + str(listindex)
                + ".MarketplaceId"
            ] = marketplace_id
            data_unsorted[
                "FeesEstimateRequestList.FeesEstimateRequest."
                + str(listindex)
                + ".IdType"
            ] = "ASIN"
            data_unsorted[
                "FeesEstimateRequestList.FeesEstimateRequest."
                + str(listindex)
                + ".IdValue"
            ] = cur_product.asin
            data_unsorted[
                "FeesEstimateRequestList.FeesEstimateRequest."
                + str(listindex)
                + ".IsAmazonFulfilled"
            ] = "true"
            data_unsorted[
                "FeesEstimateRequestList.FeesEstimateRequest."
                + str(listindex)
                + ".Identifier"
            ] = datetime.datetime.now().isoformat()
            data_unsorted[
                "FeesEstimateRequestList.FeesEstimateRequest."
                + str(listindex)
                + ".PriceToEstimateFees.ListingPrice.CurrencyCode"
            ] = "EUR"
            data_unsorted[
                "FeesEstimateRequestList.FeesEstimateRequest."
                + str(listindex)
                + ".PriceToEstimateFees.ListingPrice.Amount"
            ] = cur_product.price

            listindex = listindex + 1

        # the data has to be sorted in natural byte ordering by parameter name
        data_sorted = {}
        for cur_key in sorted(data_unsorted.keys()):
            data_sorted[cur_key] = data_unsorted[cur_key]

        # create the request signature
        req = requests.Request("POST", url=self.mws_endpoint, data=data_sorted)
        prepped = req.prepare()

        # create the query string for the request signature
        query_string = (
            "POST\nmws-eu.amazonservices.com\n/Products/2011-10-01\n" + prepped.body
        )
        signature = hmac.new(
            bytes(self.secret_key, "utf-8"),
            bytes(query_string, "utf-8"),
            digestmod="SHA256",
        ).digest()

        # add the signature to the request
        data_sorted["Signature"] = base64.b64encode(signature).decode()

        # create the request to send
        req = requests.Request("POST", url=self.mws_endpoint, data=data_sorted)
        prepped = req.prepare()
        with requests.Session() as session:
            response = session.send(prepped)

        # now parse the response text
        bs = BeautifulSoup(response.text, "xml")

        result = {}
        try:
            for cur_result in bs.find_all("FeesEstimateResult"):
                try:
                    cur_asin = cur_result.find("IdValue").string
                    cur_fee = Decimal(
                        cur_result.find("TotalFeesEstimate").Amount.string
                    )
                    result[cur_asin] = {"total": cur_fee}

                    fba_fees_tag = cur_result.find("FeeType", string="FBAFees")
                    if fba_fees_tag is None:
                        continue

                    fba_fee = Decimal(
                        fba_fees_tag.next_sibling.next_sibling.find(
                            "FinalFee"
                        ).Amount.string
                    )
                    result[cur_asin]["fba"] = fba_fee

                    closing_fee_tag = cur_result.find(
                        lambda tag: tag.find(
                            "FeeType", string="VariableClosingFee", recursive=False
                        )
                        is not None
                    )
                    if closing_fee_tag is None:
                        continue
                    closing_fee = Decimal(closing_fee_tag.FinalFee.Amount.string)
                    result[cur_asin]["closing"] = closing_fee
                except:
                    pass
        except Exception as e:
            print("Error while requesting fees! Response:")
            print(response.text)
            raise e

        return result


if __name__ == "__main__":
    fees_api = FeesAPI(
        settings.AMAZON_MWS["AWS_ACCESS_KEY_ID"],
        settings.AMAZON_MWS["SECRET_KEY"],
        settings.AMAZON_MWS["SELLER_ID"],
        settings.AMAZON_MWS["MWS_AUTH_TOKEN"],
    )

    marketplace_id_germany = "A1PA6795UKMFR9"

    class TestProduct:
        asin = "B00BIPK4AW"
        price = Decimal(32.4)

    test_product = TestProduct()
    result = fees_api.get_my_fees_estimate(marketplace_id_germany, [test_product])

    print(result)

    test_product.asin = "B07YCSBSHX"
    test_product.price = Decimal(49.99)

    result = fees_api.get_my_fees_estimate(marketplace_id_germany, [test_product])

    print(result)

    test_product.asin = "B001B1F8WW"
    test_product.price = Decimal(4.31)

    result = fees_api.get_my_fees_estimate(marketplace_id_germany, [test_product])

    print(result)

    session = Session()

    query = session.query(ProductAmazon).filter_by(asin="B001B1F8WW")
    for cur_product in query:
        print(cur_product)
        fees_response = fees_api.get_my_fees_estimate(
            marketplace_id_germany, [cur_product]
        )
        print(fees_response)

    session.close()
