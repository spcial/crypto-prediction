#!/usr/bin/python
from . import helpers

from tornado import httpserver
from tornado import gen
from tornado.ioloop import IOLoop
import tornado.web
import json

class MainHandler(tornado.web.RequestHandler):
    def post(self):
        print("POST received from IP {0}".format(self.request.remote_ip))

        response = {'error': False, 'msg': ""}
        request = json.loads(self.request.body.decode('utf-8'))

        if "token" not in request or request["token"] != "abc":
            response["msg"] = "Wrong token - no access granted"
            self.write(json.dumps(response))
            return

        if "command" in request:
            print("Command received: {0}".format(request["command"]))
            response["msg"] = "All good - command received"

        self.write(json.dumps(response))

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


def main():
    app = Application()
    app.listen(666)
    IOLoop.instance().start()


def exists():
    return True


if __name__ == '__main__':
        print("Starting arbitrage bot...")
        main()