#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import tornado.httpserver
import tornado.ioloop
import tornado.options

from tornado.options import define, options
from redisadmin import Application


def main():
    define("host", default='127.0.0.1', help="Set binding host", type=str)
    define("port", default=9000, help="Set listing port", type=int)
    tornado.options.parse_command_line()

    print('server started. visit http://{}:{}'.format(options.host, options.port))
    http_server = tornado.httpserver.HTTPServer(Application(), xheaders=True)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()
