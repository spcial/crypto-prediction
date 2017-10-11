#!/usr/bin/python

import tornado.escape, tornado.httpclient
import tornado.httpclient
from tornado import gen
import time
from collections import defaultdict


@gen.coroutine
def update_market_data_for_basecoin(basecoin):
    global market_data
    market_data = defaultdict(list)
    market_requests = []

    @gen.coroutine
    def call_market_data(url, response_handler):
        http_client = tornado.httpclient.AsyncHTTPClient()
        response = yield http_client.fetch(url)
        return response_handler(response)

    """
    Bittrex
    """
    def handle_response_bittrex(response):
        if response.error:
            print("Error: %s" % response.error)
            return False

        else:
            print("Response received from Bittrex - handling now!")
            response_data = tornado.escape.json_decode(response.body)

            for market in response_data["result"]:
                base, target = market["MarketName"].split("-")
                if base == basecoin:
                    market_data[target].append({"Bittrex": market["Last"]})

            return True

    market_requests.append(
        call_market_data(
            "https://bittrex.com/api/v1.1/public/getmarketsummaries",
            handle_response_bittrex))

    """
    Poloniex
    """
    def handle_response_poloniex(response):
        if response.error:
            print("Error: %s" % response.error)
            return False

        else:
            print("Response received from Poloniex - handling now!")
            response_data = tornado.escape.json_decode(response.body)

            for market in response_data:
                base, target = market.split("_")
                if base == basecoin:
                    market_data[target].append({"Poloniex": response_data[market]["last"]})


            return True

    market_requests.append(
        call_market_data(
            "https://poloniex.com/public?command=returnTicker",
            handle_response_poloniex))

    """
        Kraken
    """
    def handle_response_kraken(response):
        if response.error:
            print("Error: %s" % response.error)
            return False

        else:
            print("Response received from Kraken - handling now!")
            response_data = tornado.escape.json_decode(response.body)
            import re

            for market in response_data["result"]:
                base = "ETH"
                target = re.findall('XBT|EOS|GNO|ETC|ICN|REP|MLN', market, re.DOTALL)

                if base == basecoin:
                    market_data[target[0]].append({"Kraken": response_data["result"][market]["c"][0]})

            return True

    market_requests.append(
        call_market_data(
            "https://api.kraken.com/0/public/Ticker?pair=ETHXBT,EOSETH,GNOETH,ETCETH,ICNETH,REPETH,MLNETH",
            handle_response_kraken))



    print("--- Retrieve market data now ---")
    start_time = time.time()
    response_dict = yield market_requests
    print("--- Marked data updated in {0} seconds. Responses: {1} ---".format(time.time() - start_time, response_dict))
