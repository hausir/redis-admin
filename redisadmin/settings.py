# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import os

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

    'redis_server': True,
    'redis_db': 16,

    # If set to None or 0 the session will be deleted when the user closes the browser.
    # If set number the session lives for value days.
    'permanent_session_lifetime': 1,

    'per_page': 100,
}
