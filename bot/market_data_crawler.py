#!/usr/bin/python

import tornado.escape
import tornado.httpclient
import tornado.httpclient
from tornado import gen
import time
from collections import defaultdict

market_data = defaultdict(list)


@gen.coroutine
def update_market_data_for_basecoin(basecoin):
    market_requests = []

    @gen.coroutine
    def call_market_data(url, response_handler):
        start_time5 = time.time()
        http_client = tornado.httpclient.AsyncHTTPClient()
        response = yield http_client.fetch(url)
        print("Data received for url {0}. Responsetime: {1:.2f}ms".format(url[0:15], (time.time() - start_time5)*100))
        return response_handler(response)

    """
    Bittrex
    """
    def handle_response_bittrex(response):
        if response.error:
            print("Error: %s" % response.error)
            return False

        else:
            start_time1 = time.time()
            response_data = tornado.escape.json_decode(response.body)

            for market in response_data["result"]:
                base, target = market["MarketName"].split("-")
                if base == basecoin:
                    market_data[target].append({"Bittrex": market["Last"]})
                elif target == basecoin:
                    market_data[base].append({"Bittrex": market["Last"]})

            print("Handling bitr finished in {:.3f}ms".format((time.time() - start_time1)*100))
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
            start_time2 = time.time()
            response_data = tornado.escape.json_decode(response.body)

            for market in response_data:
                base, target = market.split("_")
                if base == basecoin:
                    market_data[target].append({"Poloniex": response_data[market]["last"]})
                elif target == basecoin:
                    market_data[base].append({"Poloniex": response_data[market]["last"]})

            print("Handling pol finished in {:.3f}ms".format((time.time() - start_time2)*100))
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
            start_time3 = time.time()
            response_data = tornado.escape.json_decode(response.body)
            import re

            for market in response_data["result"]:
                base = "ETH"
                target = re.findall('XBT|EOS|GNO|ETC|ICN|REP|MLN', market, re.DOTALL)

                if target[0] == "XBT":
                    target[0] = "BTC"

                if base == basecoin:
                    market_data[target[0]].append({"Kraken": response_data["result"][market]["c"][0]})

            print("Handling kra finished in {:.3f}ms".format((time.time() - start_time3)*100))
            return True

    market_requests.append(
        call_market_data(
            "https://api.kraken.com/0/public/Ticker?pair=ETHXBT,EOSETH,GNOETH,ETCETH,ICNETH,REPETH,MLNETH",
            handle_response_kraken))

    """
        Bitfinex
    """
    def handle_response_bitfinex(response):
        if response.error:
            print("Error: %s" % response.error)
            return False

        else:
            start_time4 = time.time()
            response_data = tornado.escape.json_decode(response.body)
            import re

            for market in response_data:
                base = "ETH"
                target = re.findall('BTC|IOT|EOS|SAN|OMG|QTM|AVT|ETP|NEO|BCH', market[0], re.DOTALL)

                if base == basecoin:
                    market_data[target[0]].append({"Bitfinex": market[7]})

            print("Handling bitf finished in {:.3f}ms".format((time.time() - start_time4)*100))
            return True

    market_requests.append(
        call_market_data(
            "https://api.bitfinex.com/v2/tickers?symbols=tETHBTC,tIOTETH,tEOSETH,tSANETH,tOMGETH,tQTMETH,tAVTETH,tETPETH,tNEOETH,tBCHETH",
            handle_response_bitfinex))

    print("--- Retrieve market data now ---")
    start_time = time.time()
    response_dict = yield market_requests
    print("--- Marked data updated in {0:.3f}s. Responses: {1} ---".format(time.time() - start_time, response_dict))
