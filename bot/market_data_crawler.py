#!/usr/bin/python

from tornado import gen
from collections import defaultdict

import sys
import time
import asyncio
import ccxt.async as ccxt

market_data = defaultdict(list)


def style(s, style):
    return style + s + '\033[0m'


def green(s):
    return style(s, '\033[92m')


def blue(s):
    return style(s, '\033[94m')


def yellow(s):
    return style(s, '\033[93m')


def red(s):
    return style(s, '\033[91m')


def pink(s):
    return style(s, '\033[95m')


def bold(s):
    return style(s, '\033[1m')


def underline(s):
    return style(s, '\033[4m')


def dump(*args):
    print(' '.join([str(arg) for arg in args]))

proxies = [
    '',  # no proxy by default
    'https://cors-anywhere.herokuapp.com/',

]


def update_market_data_for_symbol_and_exchange(allowed_symbols, exchanges):
    if len(exchanges) > 1:
        start_time = time.time()
        ids = list(exchanges)
        exchanges = {}

        dump(yellow('Loading'), 'market data for following exchanges:', ' '.join(ids))

        for id in ids:
            # instantiate the exchange by id
            exchange = getattr(ccxt, id)()

            # save it in a dictionary under its id for future use
            exchanges[id] = exchange

        exchanges = fetch_all_markets(exchanges)

        allSymbols = [symbol for id in ids for symbol in exchanges[id].symbols]

        # get all unique symbols
        uniqueSymbols = list(set(allSymbols))

        # filter out symbols that are not present on at least two exchanges
        arbitrableSymbols = sorted([symbol for symbol in uniqueSymbols if allSymbols.count(symbol) > 1])

        exchanges = fetch_all_order_books(exchanges, arbitrableSymbols)

        dump(green('Finished!'), 'Responsetime:', red("{:.2f}ms".format((time.time() - start_time) * 100)))

        with open("market_data.txt", "w") as file:
            for key, value in market_data.items():
                file.write("\nMarket: {}".format(key))

                for order_book in value:
                    file.write("\n    Order Book: {0}".format(order_book))

        return market_data
    else:
        dump(red("Invalid number of arguments given"))
        return None


def fetch_all_order_books(exchanges, arbitrableSymbols):
    ob_start_time = time.time()

    async def fetch_single_order_books(exchange, arbitrableSymbols):
        dump(yellow('Retrieving'), 'order books from exchange', yellow(exchange.id))

        order_books = []
        available_symbols = (symbol for symbol in arbitrableSymbols if symbol in exchange.symbols)

        for symbol in available_symbols:
            # basic round-robin proxy scheduler
            currentProxy = -1
            maxRetries = len(proxies)

            for numRetries in range(0, maxRetries):
                # try proxies in round-robin fashion
                currentProxy = (currentProxy + 1) % len(proxies)

                try:  # try to load exchange markets using current proxy

                    tmp_order_book = await exchange.fetch_order_book(symbol)
                    tmp_order_book['symbol'] = symbol
                    order_books.append(tmp_order_book)
                    break

                except ccxt.DDoSProtection as e:
                    dump(yellow(type(e).__name__), e.args)
                    await asyncio.sleep(exchange.rateLimit / 500)
                except ccxt.RequestTimeout as e:
                    dump(yellow(type(e).__name__), e.args)
                except ccxt.AuthenticationError as e:
                    dump(yellow(type(e).__name__), e.args)
                except ccxt.ExchangeNotAvailable as e:
                    dump(yellow(type(e).__name__), e.args)
                except ccxt.ExchangeError as e:
                    dump(yellow(type(e).__name__), e.args)
                except ccxt.NetworkError as e:
                    dump(yellow(type(e).__name__), e.args)
                except Exception as e:  # reraise all other exceptions
                    raise

        dump("Order book for", yellow(str(exchange.id)), "retrieved in", red("{:.2f}ms".format((time.time() - ob_start_time) * 100)))
        market_data[exchange.id] = order_books

    async_executor = []
    for key, value in exchanges.items():
        # add future to list
        async_executor.append(asyncio.ensure_future(fetch_single_order_books(exchanges[key], arbitrableSymbols)))

    # wait till all futures in list completed
    asyncio.get_event_loop().run_until_complete(asyncio.gather(*async_executor))

    return exchanges


def fetch_all_markets(exchanges):
    start_time_markets = time.time()

    async def fetch_single_market(exchange):
        # basic round-robin proxy scheduler
        currentProxy = -1
        maxRetries = len(proxies)

        for numRetries in range(0, maxRetries):
            # try proxies in round-robin fashion
            currentProxy = (currentProxy + 1) % len(proxies)

            try:  # try to load exchange markets using current proxy

                exchange.proxy = proxies[currentProxy]
                await exchange.load_markets()
                break

            except ccxt.DDoSProtection as e:
                dump(yellow(type(e).__name__), e.args)
            except ccxt.RequestTimeout as e:
                dump(yellow(type(e).__name__), e.args)
            except ccxt.AuthenticationError as e:
                dump(yellow(type(e).__name__), e.args)
            except ccxt.ExchangeNotAvailable as e:
                dump(yellow(type(e).__name__), e.args)
            except ccxt.ExchangeError as e:
                dump(yellow(type(e).__name__), e.args)
            except ccxt.NetworkError as e:
                dump(yellow(type(e).__name__), e.args)
            except Exception as e:  # reraise all other exceptions
                raise

        dump(green(exchange.id), 'loaded', green(str(len(exchange.symbols))), 'markets')

    async_executor = []
    for key, value in exchanges.items():
        # add future to list
        async_executor.append(asyncio.ensure_future(fetch_single_market(exchanges[key])))

    # wait till all futures in list completed
    asyncio.get_event_loop().run_until_complete(asyncio.gather(*async_executor))

    dump(green('Loaded all markets!'), 'Responsetime:', red("{:.2f}ms".format((time.time() - start_time_markets) * 100)))

    return exchanges


if __name__ == '__main__':
    update_market_data_for_symbol_and_exchange(None, sys.argv[1:])
