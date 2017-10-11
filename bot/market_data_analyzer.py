#!/usr/bin/python
from . import market_data_crawler

import time
import operator


def calculate_arbitrage_opportunities(basecoin):
    market_data = market_data_crawler.market_data
    print("Total currency pairs: {0}".format(len(market_data)))
    market_opport = {}

    print("--- Calculating arbitrage oportunities now ---")
    start_time = time.time()

    for pair in market_data:
        if len(market_data[pair]) > 1:
            price_list = {}

            for price in market_data[pair]:
                key, value = price.popitem()
                price_list[key] = float(value)

            sorted_x = sorted(price_list.items(), key=operator.itemgetter(1), reverse=True)
            spread = sorted_x[0][1] - sorted_x[-1][1]
            spread_perc = round((spread / sorted_x[0][1]) * 100, 2)

            market_opport[pair] = {"highest_market": sorted_x[0][0],
                                   "highest_price:": sorted_x[0][1],
                                   "lowest_market": sorted_x[-1][0],
                                   "lowest_price": sorted_x[-1][1],
                                   "spread": spread,
                                   "spread_perc": spread_perc,
                                   "pair": pair}

    market_opport = sorted(market_opport.values(), key=operator.itemgetter("spread_perc"), reverse=True)

    print("--- Arbitrage oportunities calculated in {0:.3f}ms ---".format((time.time() - start_time)*100))

    return market_opport
