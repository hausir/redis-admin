# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import os
import redis
import logging
import tornado.web
import tornado.locale
import tornado.escape
import tornado.ioloop

from pygments import highlight
from pygments.lexers import get_lexer_for_filename
from pygments.formatters.html import HtmlFormatter
from redisadmin.forms import create_forms
from redisadmin.extensions.sessions import RedisSession


class RequestHandler(tornado.web.RequestHandler):
    title = 'Welcome'

    def data_received(self, chunk):
        pass

    def initialize(self):
        db = self.session['db'] if 'db' in self.session else 0
        self.redis = redis.StrictRedis(
            host=self.settings.get('redis_host'),
            port=self.settings.get('redis_port'),
            password=self.settings.get('redis_password'),
            db=db, decode_responses=True
        )

    def get_current_user(self):
        return self.session['user']

    @property
    def session(self):
        if not hasattr(self, '_session'):
            expires = self.settings.get('session_expires')
            sessionid = self.get_secure_cookie('sid')
            if isinstance(sessionid, bytes):
                sessionid = sessionid.decode()
            self._session = RedisSession(sessionid, expires=expires)
            if not sessionid:
                self.set_secure_cookie('sid', self._session.id, expires_days=expires)

        return self._session

    def get_user_locale(self):
        code = self.get_cookie('lang', self.settings.get('default_locale', 'zh_CN'))
        return tornado.locale.get(code)

    def get_error_html(self, status_code, **kwargs):
        if self.settings.get('debug', False) is False:
            self.set_status(status_code)
            return self.render_string('errors/%s.html' % status_code)

        else:
            def get_snippet(fp, target_line, num_lines):
                if fp.endswith('.html'):
                    fp = os.path.join(self.get_template_path(), fp)

                half_lines = (num_lines / 2)
                try:
                    with open(fp) as f:
                        all_lines = [line for line in f]
                        code = ''.join(all_lines[target_line - half_lines - 1:target_line + half_lines])
                        formatter = HtmlFormatter(linenos=True, linenostart=target_line - half_lines,
                                                  hl_lines=[half_lines + 1])
                        lexer = get_lexer_for_filename(fp)
                        return highlight(code, lexer, formatter)

                except Exception as ex:
                    logging.error(ex)
                    return ''

            css = HtmlFormatter().get_style_defs('.highlight')
            exception = kwargs.get('exception', None)
            return self.render_string('errors/exception.htm',
                                      get_snippet=get_snippet,
                                      css=css,
                                      exception=exception,
                                      status_code=status_code,
                                      kwargs=kwargs)

    def get_args(self, key, default=None, _type=None):
        if _type == list:
            if default is None:
                default = []
            return self.get_arguments(key, default)
        value = self.get_argument(key, default)
        if value and _type:
            try:
                value = _type(value)
            except ValueError:
                value = default
        return value

    @property
    def is_xhr(self):
        """
        True if the request was triggered via a JavaScript XMLHttpRequest.
        This only works with libraries that support the `X-Requested-With`
        header and set it to "XMLHttpRequest".  Libraries that do that are
        prototype, jQuery and Mochikit and probably some more.
        """

        return self.request.headers.get('X-Requested-With', '') \
                   .lower() == 'xmlhttprequest'

    @property
    def forms(self):
        return create_forms(self.get_user_locale().code)

    def _(self, message, plural_message=None, count=None):
        return self.locale.translate(message, plural_message, count)


class ErrorHandler(RequestHandler):
    """raise 404 error if url is not found.
    fixed tornado.web.RequestHandler HTTPError bug.
    """

    def prepare(self):
        self.set_status(404)
        raise tornado.web.HTTPError(404)
