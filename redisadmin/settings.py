# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import os

from redisadmin.extensions.jinja2 import loader

settings = {
    'debug': True,
    'cookie_secret': 'simple',
    'login_url': '/login',
    'xsrf_cookies': True,

    'username': 'admin',
    'password': '111',

    'template_path': os.path.join(os.path.dirname(__file__), 'templates'),
    'static_path': os.path.join(os.path.dirname(__file__), 'static'),

    'default_locale': 'zh_CN',

    'redis_host': 'localhost',
    'redis_port': 6379,
    'redis_password': None,
    'redis_db': 16,

    'session_db': 0,
    'session_expires': 86400,

    'per_page': 100,
    'autoescape': None,

    'template_loader': loader,
}
