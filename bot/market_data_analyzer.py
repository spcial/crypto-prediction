#!/usr/bin/python
from . import market_data_crawler
from bot.shared_config import *

import time
import sys
import operator
import pprint


def calculate_arbitrage_opportunities(exchanges):
    start_time = time.time()
    market_data = market_data_crawler.update_market_data_for_symbol_and_exchange(exchanges)
    sorted_market_data = {}

    for exchange_name, order_books in market_data.items():
        for order_book in order_books:
            symbol = order_book['symbol']
            new_dictionary = {symbol:
                                  {exchange_name:
                                       {"bids": order_book['bids'][:5],
                                        "asks": order_book['asks'][:5],
                                        "timestamp": order_book['timestamp']}}}
            if symbol not in sorted_market_data.keys():
                sorted_market_data.update(new_dictionary)
            else:
                sorted_market_data[symbol].update(new_dictionary[symbol])

    dump(green(str(len(sorted_market_data))), "possible symbols found in total:", ' '.join(sorted_market_data.keys()))

    market_opport = {}
    for symbol, exchanges in sorted_market_data.items():
        lowest_ask = None
        highest_bid = None
        market_opport.update({symbol: {}})
        for exchange_name, order_book in exchanges.items():
            if lowest_ask is None or lowest_ask['value'] < order_book['asks'][0]:
                lowest_ask = {"exchange_name":exchange_name,
                               "value":order_book['asks'][0],
                               "order_book": order_book['asks'][:3]}

            if highest_bid is None or highest_bid['value'] > order_book['bids'][0]:
                highest_bid = {"exchange_name": exchange_name,
                               "value": order_book['bids'][0],
                               "order_book": order_book['bids'][:3]}

        spread = float(highest_bid['value'][0]) - float(lowest_ask['value'][0])

        market_opport[symbol].update({"highest_bid": highest_bid,
                                      "lowest_ask": lowest_ask,
                                      "spread": spread,
                                      "spread_perc": round((spread / float(highest_bid['value'][0])) * 100, 2),
                                      "symbol": symbol})

        if spread > 0:
            with open("market_opportunity_found.txt", "a") as file:
                file.write("\n+n--- Arbitrage oppportunity found! ---\n\n")
                pprint.pprint(market_opport[symbol], stream=file)

    sorted_list = sorted(market_opport.values(), key=operator.itemgetter("spread_perc"), reverse=True)

    with open("market_analyzation.txt", "w") as file:
        pprint.pprint(sorted_list, stream=file)

    print("--- Arbitrage oportunities calculated in {0:.3f}ms ---".format((time.time() - start_time)*100))

    return market_opport

if __name__ == '__main__':
    calculate_arbitrage_opportunities(sys.argv[1:])
