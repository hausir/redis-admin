# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import os
import redis
import tornado.web
import tornado.locale

from redisadmin import uimodules
from redisadmin.settings import settings
from redisadmin.forms import create_forms
from redisadmin.views import ErrorHandler, frontend
from redisadmin.extensions.routing import Route
from redisadmin.extensions.sessions import RedisSessionStore


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
                       # other handlers...
                   ] + Route.routes()

        # Custom 404 ErrorHandler
        handlers.append((r"/(.*)", ErrorHandler))

        settings.update(dict(
            ui_modules=uimodules,
            autoescape=None
        ))

        if 'default_locale' in settings:
            path = os.path.join(os.path.dirname(__file__), 'translations')
            tornado.locale.load_translations(path)

        tornado.web.Application.__init__(self, handlers, **settings)

        self.forms = create_forms()
        self.redis = [redis.StrictRedis(db=n, decode_responses=True) for n in range(self.settings['redis_db'])]
        self.session_store = RedisSessionStore(self.redis[0])
