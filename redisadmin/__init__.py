# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import os
import tornado.web
import tornado.locale

from redisadmin.settings import settings
from redisadmin.urls import url_patterns


class Application(tornado.web.Application):
    def __init__(self):
        path = os.path.join(os.path.dirname(__file__), 'translations')
        tornado.locale.load_translations(path)
        tornado.web.Application.__init__(self, url_patterns, **settings)
