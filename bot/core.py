#!/usr/bin/python
from . import market_data_crawler, market_data_analyzer

from tornado import gen
from tornado.ioloop import IOLoop
import tornado.web
import json
import sys


class MainHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def post(self):
        print("POST received from IP {0}".format(self.request.remote_ip))

        response = {'error': False, 'msg': "None"}
        request = json.loads(self.request.body.decode('utf-8'))

        if "token" not in request or request["token"] != "abc":
            response["msg"] = "Wrong token - no access granted"
            self.write(json.dumps(response))
            return

        if "command" in request:
            print("Command received: {0}".format(request["command"]))

            if request["command"] == "init_market_data":
                yield self.update_market_data(request, response)
            elif request["command"] == "get_market_data":
                yield self.get_market_data(request, response)
            elif request["command"] == "calc_arbitr_opport":
                yield self.update_market_data(request, response)
                yield self.get_arbitrage_opportunities(request, response)

        self.write(json.dumps(response))

    @gen.coroutine
    def update_market_data(self, request, response):
        yield market_data_crawler.update_market_data_for_basecoin(request["basecoin"])
        response["msg"] = "Market Data initialized"
        response["data"] = market_data_crawler.market_data

    @gen.coroutine
    def get_market_data(self, request, response):
        response["msg"] = "Market Data Retrieved"
        response["data"] = market_data_crawler.market_data

    @gen.coroutine
    def get_arbitrage_opportunities(self, request, response):
        response["msg"] = "Arbitrage Oportunities Retrieved"
        response["data"] = market_data_analyzer.calculate_arbitrage_opportunities(request["basecoin"])

    @gen.coroutine
    def delete(self):
        print("Stopping server...")

        response_json = json.dumps({'error': False, 'msg': "Server stopped"})
        self.write(response_json)

        IOLoop.instance().stop()


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/?", MainHandler)
        ]
        tornado.web.Application.__init__(self, handlers)


def main(port):
    app = Application()
    app.listen(port)
    IOLoop.instance().start()


def exists():
    return True


if __name__ == '__main__':
        port = int(sys.argv[1])
        print("Starting arbitrage bot on port {0}...".format(port))
        main(port)