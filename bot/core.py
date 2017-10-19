#!/usr/bin/python
from . import market_data_crawler, market_data_analyzer, shared_config

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

        if "token" not in request or request["token"] != "den":
            response["msg"] = "Wrong token - no access granted"
            self.write(json.dumps(response))
            return

        if "command" in request:
            print("Command received: {0}".format(request["command"]))

            if request["command"] == "start_bot":
                shared_config.run_bot = True
            elif request["command"] == "stop_bot":
                shared_config.run_bot = False
            else:
                response["msg"] = "Unknown command"

        self.write(json.dumps(response))

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


@gen.coroutine
def run_bot():
    while True:
        yield gen.sleep(30)
        if shared_config.run_bot:
            market_data_analyzer.calculate_arbitrage_opportunities(['kraken', 'bitfinex', 'binance', 'hitbtc', 'gdax', 'bittrex', 'poloniex'])


def main(port):
    app = Application()
    app.listen(port)
    run_bot()
    IOLoop.instance().start()


if __name__ == '__main__':
        port = int(sys.argv[1])
        print("Starting arbitrage bot on port {0}...".format(port))
        main(port)
