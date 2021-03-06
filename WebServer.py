#!/usr/bin/env python
#-*-coding:utf-8-*-
import os.path
from com.changxia.common.log.basiclogger import *
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from handler.QRTestHandler import *
from tornado.options import define, options
define("port", default=8000, help="run on the given port", type=int)

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/qrtest", QRTestHandler),
        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            debug=True,
            autoescape=None
            )
        tornado.web.Application.__init__(self, handlers, **settings)




def main():
    LOGGING("webserver")
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()

