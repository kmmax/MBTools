#!/usr/bin/env python3
"""An example HTTP server with GET and POST endpoints."""

from http.server import HTTPServer, BaseHTTPRequestHandler
from http import HTTPStatus
import json
import time
from functools import partial

from MBTools.oiserver.OIServer import IOServer
from MBTools.oiserver.Tag import Tag, TagType


# Sample blog post data similar to
# https://ordina-jworks.github.io/frontend/2019/03/04/vue-with-typescript.html#4-how-to-write-your-first-component
_g_posts = [
    {
        'title': 'My first blogpost ever!',
        'body': 'Lorem ipsum dolor sit amet.',
        'author': 'Elke',
        'date_ms': 1593607500000,  # 2020 July 1 8:45 AM Eastern
    },
    {
        'title': 'Look I am blogging!',
        'body': 'Hurray for me, this is my second post!',
        'author': 'Elke',
        'date_ms': 1593870300000, # 2020 July 4 9:45 AM Eastern
    },
    {
        'title': 'Another one?!',
        'body': 'Another one!',
        'author': 'Elke',
        'date_ms': 1594419000000, # 2020 July 10 18:10 Eastern
    }
]

data = None;
with open("./sites/data.json", 'r') as f:
    data = json.load(f)

# ioserver: IOServer = None


class _RequestHandler(BaseHTTPRequestHandler):
    # def __init__(self, io: IOServer, *args):
    #     self._io: IOServer = io
    #     # BaseHTTPRequestHandler.__init__(self, *args)
    #     super(_RequestHandler, self).__init__(*args, **kwards)

    def _set_headers(self):
        self.send_response(HTTPStatus.OK.value)
        self.send_header('Content-type', 'application/json')
        # Allow requests from any origin, so CORS policies don't
        # prevent local development.
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    def do_GET(self):
        print("do_GET")
        self._set_headers()
        # self.wfile.write(json.dumps(_g_posts).encode('utf-8'))
        self.wfile.write(json.dumps(data).encode('utf-8'))
        # data2 = self.getData()
        # self.wfile.write(json.dumps(data2).encode('utf-8'))

    def do_POST(self):
        print("do_POST")
        length = int(self.headers.get('content-length'))
        message = json.loads(self.rfile.read(length))
        message['date_ms'] = int(time.time()) * 1000
        _g_posts.append(message)
        self._set_headers()
        self.wfile.write(json.dumps({'success': True}).encode('utf-8'))

    def do_OPTIONS(self):
        print("do_OPTIONS")
        # Send allow-origin header for preflight POST XHRs.
        self.send_response(HTTPStatus.NO_CONTENT.value)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST')
        self.send_header('Access-Control-Allow-Headers', 'content-type')
        self.end_headers()

    def getData(self):
        tag = None
        value = 0
        res = None
        if self._io:
            tag = self._io.tag("ST1")
            type = tag.type
            value = tag.value
            time = tag.time
            res = [{"tags":
                        {
                            "name": tag.name,
                            "address": tag.address,
                            "type": "{0}".format(tag.type),
                            "valur": "{0}".format(tag.value),
                            "quality": "{0}".format(tag.quality),
                            "time:": "{0}".format(tag.time)
                         }
                    }
                   ]
        return res


class JsonServer:
    def __init__(self, io: IOServer = None):
        self._io = io
        self.server_address = ('', 8001)
        # handler = partial(_RequestHandler, self._io)
        self.httpd = HTTPServer(self.server_address, _RequestHandler)
        # self.httpd = HTTPServer(self.server_address, handler)
        print('serving at %s:%d' % self.server_address)

    def setIoServer(self, oi: IOServer):
        self._io = oi
        print("JsonServer: {0}".format(self._io.tag("ST1")))

    def start(self):
        self.httpd.serve_forever()


def run_server():
    srv = JsonServer()
    srv.start()


if __name__ == '__main__':
    run_server()