import tornado.escape, tornado.httpclient

def update_market_data_for_basecoin(basecoin):
    global market_data
    market_data = {}
    market_requests = []

    """Bittrex"""

    def handle_response_bittrex(response):
        if response.error:
            print("Error: %s" % response.error)
        else:
            response_data = tornado.escape.json_decode(response.body)

            for market in response_data["result"]:
                base, target = market["MarketName"].split("-")
                if base == basecoin:
                    market_data.update({
                        target: {
                            "Bittrex": market["Last"]
                        }
                    })


    bittrex = {
        "url": "https://bittrex.com/api/v1.1/public/getmarketsummaries",
        "response_handler": handle_response_bittrex
    }

    market_requests.append(bittrex)

    http_client = tornado.httpclient.AsyncHTTPClient()
    for request in market_requests:
        print("Doing request to {0}".format(request["url"]))
        http_client.fetch(request["url"], request["response_handler"])

