# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import json
import logging
import tornado.web

from redis.exceptions import RedisError
from redisadmin.views import RequestHandler
from redisadmin.helpers import Pagination


class Index(RequestHandler):
    @tornado.web.authenticated
    def get(self):
        self.title = self._('Redis web manager by tornado')
        self.render('index.html')
        return


class Connection(RequestHandler):
    @tornado.web.authenticated
    def get(self):
        db = self.get_args('db', 0, _type=int)

        self.session['db'] = db
        self.session.save()

        self.write(dict(success=True))
        return


class Menu(RequestHandler):
    @tornado.web.authenticated
    def get(self):
        q = self.get_args('q', '*')

        fullkeys = [key for key in self.redis.keys(q)]

        def get_item(key, root):
            _id = '%s:%s' % (root, key) if root else key
            _children = get_children(_id)

            item = {
                "text": '%s(%s)' % (_id, len(_children)) if _children else _id,
                "id": _id,
                "children": sorted(_children, key=lambda x: x.get('id'))[:200]
            }
            return item

        def get_children(root=None):
            if root:
                keys = set(
                    sorted(
                        [key[len(root) + 1:].split(':')[0] for key in fullkeys if key[:len(root) + 1] == '%s:' % root]
                    )
                )
            else:
                keys = set(sorted([key.split(':')[0] for key in fullkeys]))

            return [get_item(key, root) for key in keys]

        children = get_children()
        while len(children) == 1 and children[0]['children']:
            children = children[0]['children']

        menu = [{"text": '%s(%s)' % (q, len(children)), "id": q, "children": children}]

        self.write(json.dumps(menu))
        return


class New(RequestHandler):
    @tornado.web.authenticated
    def get(self):
        key = self.get_args('key')
        _type = self.get_args('type')
        value = self.get_args('value')

        if key and value and _type in ['string', 'hash', 'list', 'set', 'zset']:

            if self.redis.exists(key):
                self.write(dict(success=False, error=u"Key is exists!"))
                return

            if _type == 'string':
                self.redis.set(key, value)

            elif _type == 'hash':
                try:
                    value = json.loads(value)
                except ValueError:
                    self.error()
                    return
                else:
                    if isinstance(value, dict):
                        for field, v in value.items():
                            self.redis.hset(key, field, str(v))
                    else:
                        self.error()
                        return

            elif _type == 'list':
                try:
                    value = json.loads(value)
                except ValueError:
                    self.error()
                    return
                else:
                    if isinstance(value, list):
                        for v in value:
                            self.redis.rpush(str(v))
                    else:
                        self.error()
                        return

            elif _type == 'set':
                try:
                    value = json.loads(value)
                except ValueError:
                    self.error()
                    return
                else:
                    if isinstance(value, list):
                        for v in value:
                            self.redis.sadd(str(v))
                    else:
                        self.error()
                        return

            elif _type == 'zset':
                score = self.get_args('score')
                if score:
                    self.redis.zadd(key, score, value)
                else:
                    self.error()
                    return

            self.write(dict(success=True))
            return

        self.error()
        return

    def error(self):
        self.write(dict(success=False, error="New key create failed, check form and value is valid."))
        return


class Value(RequestHandler):
    @tornado.web.authenticated
    def get(self):
        key = self.get_args('key', '')
        if key:
            _type = self.redis.type(key)
            if _type == 'string':
                value = self.get_strings(key)
            elif _type == 'list':
                value = self.get_lists(key)
            elif _type == 'hash':
                value = self.get_hashes(key)
            elif _type == 'set':
                value = self.get_sets(key)
            elif _type == 'zset':
                value = self.get_sortedsets(key)
            else:
                _type = value = None
            print(value)
            self.write(dict(type=_type, key=key, value=value))
            return

        self.write(dict(type=None, key=key, value=None))
        return

    def get_strings(self, key):
        return self.redis.get(key)

    def get_hashes(self, key):
        return self.redis.hgetall(key)

    def get_lists(self, key):
        return self.redis.lrange(key, 0, -1)

    def get_sets(self, key):
        return list(self.redis.smembers(key))

    def get_sortedsets(self, key):
        return list(self.redis.zrange(key, 0, -1))


class List(RequestHandler):
    @tornado.web.authenticated
    def get(self):
        root = self.get_args('root', '')
        if root:

            while root and root[-1] in [':', '*']:
                root = root[:-1]

            page = self.get_args('page', 1, _type=int)
            if page < 1:
                page = 1

            per_page = self.settings['per_page']

            fullkeys = sorted(self.redis.keys(root + ':*'))

            data = [(key, self.redis.hgetall(key) if self.redis.type(key) == 'hash' else {}) for key in fullkeys if
                    key.split(root)[-1].count(':') == 1]

            page_obj = Pagination(data, page, per_page=per_page)

            iter_pages = [p for p in page_obj.iter_pages()]

            self.write(dict(data=page_obj.items, root=root, page=page, iter_pages=iter_pages))
            return

        self.write(dict(data=[]))
        return


class Info(RequestHandler):
    @tornado.web.authenticated
    def get(self):
        info = self.redis.info()
        self.write(json.dumps(list(info.items())))
        return


class FlushDB(RequestHandler):
    @tornado.web.authenticated
    def get(self):
        result = self.redis.flushdb()
        self.write(dict(success=result))
        return


class FlushAll(RequestHandler):
    @tornado.web.authenticated
    def get(self):
        result = self.redis.flushall()
        self.write(dict(success=result))
        return


class Expire(RequestHandler):
    @tornado.web.authenticated
    def get(self):
        key = self.get_args('key', '')
        seconds = self.get_args('seconds', 0, _type=int)

        if key:
            result = self.redis.expire(key, seconds)

            self.write(dict(success=result))
            return

        self.write(dict(success=False))
        return


class Move(RequestHandler):
    @tornado.web.authenticated
    def get(self):

        key = self.get_args('key', '')
        db = self.get_args('db', -1, _type=int)

        if key and db >= 0:
            try:
                result = self.redis.move(key, db)
            except RedisError:
                result = False

            self.write(dict(success=result))
            return

        self.write(dict(success=False))
        return


class Edit(RequestHandler):
    @tornado.web.authenticated
    def get(self):

        key = self.get_args('key', '')
        index = self.get_args('index', '')
        field = self.get_args('field', '')
        value = self.get_args('value', '')

        if key:

            if self.redis.exists(key):

                _type = self.redis.type(key)

                if _type == 'string':
                    result = self.edit_strings(key, value)
                elif _type == 'list':
                    result = self.edit_lists(key, index, value)
                elif _type == 'hash':
                    result = self.edit_hashs(key, index, value)
                elif _type == 'set':
                    result = self.edit_sets(key, field, value)
                elif _type == 'zset':
                    result = self.edit_sortedsets(key, field, value)
                else:
                    logging.error('Unexpected key type by %s' % key)
                    result = False

                self.write(dict(success=result))
                return

        self.write(dict(success=False))
        return

    def edit_strings(self, key, value):
        return self.redis.set(key, value)

    def edit_lists(self, key, index, value):
        index = int(index) if index.isdigit() else None
        return self.redis.lset(key, index, value) if index is not None else False

    def edit_hashs(self, key, field, value):
        return self.redis.hset(key, field, value)

    def edit_sets(self, key, field, value):
        if field == value:
            return True
        self.redis.srem(key, field)
        return self.redis.sadd(key, value)

    def edit_sortedsets(self, key, field, value):
        if field == value:
            return True
        score = self.redis.zscore(key, field)
        self.redis.zrem(key, field)
        return self.redis.zadd(key, score, value)


class Add(RequestHandler):
    @tornado.web.authenticated
    def get(self):

        key = self.get_args('key', '')
        value = self.get_args('value', '')

        if key:

            if self.redis.exists(key):

                _type = self.redis.type(key)

                if _type == 'string':
                    result = self.add_strings(key, value)
                elif _type == 'list':
                    pos = self.get_args('pos', 'r')
                    result = self.add_lists(key, value, pos)
                elif _type == 'hash':
                    field = self.get_args('field', '')
                    result = self.add_hashs(key, field, value) if field else False
                elif _type == 'set':
                    result = self.add_sets(key, value)
                elif _type == 'zset':
                    score = self.get_args('score', '')
                    result = self.add_sortedsets(key, score, value) if score else False
                else:
                    logging.error('Unexpected key type by %s' % key)
                    result = False

                self.write(dict(success=result))
                return

        self.write(dict(success=False))
        return

    def add_strings(self, key, value):
        """ return a length with key """
        return self.redis.append(key, value)

    def add_lists(self, key, value, pos):
        """ return a index with key """
        if pos == 'r':
            return self.redis.rpush(key, value)
        else:
            return self.redis.lpush(key, value)

    def add_hashs(self, key, field, value):
        """ return a changed lines with key """
        return self.redis.hset(key, field, value)

    def add_sets(self, key, member):
        """ return a changed lines with key """
        return self.redis.sadd(key, member)

    def add_sortedsets(self, key, score, member):
        """ return a changed lines with key """
        return self.redis.zadd(key, score, member)


class Remove(RequestHandler):
    @tornado.web.authenticated
    def get(self):

        key = self.get_args('key', '')
        field = self.get_args('field', '')

        if key:

            if self.redis.exists(key):

                _type = self.redis.type(key)

                if _type == 'hash':
                    result = self.redis.hdel(key, field)
                elif _type == 'set':
                    result = self.redis.srem(key, field)
                elif _type == 'zset':
                    result = self.redis.zrem(key, field)
                else:
                    logging.error('Unexpected key type by %s' % key)
                    result = False

                self.write(dict(success=result))
                return

        self.write(dict(success=False))
        return


class Pop(RequestHandler):
    @tornado.web.authenticated
    def get(self):

        key = self.get_args('key', '')
        pos = self.get_args('pos', 'l')

        if key:

            if self.redis.exists(key):

                _type = self.redis.type(key)

                if _type == 'list':
                    if pos == 'r':
                        result = self.redis.rpop(key)
                    else:
                        result = self.redis.lpop(key)
                else:
                    logging.error('Can not pop by key %s' % key)
                    result = False

                self.write(dict(success=result))
                return

        self.write(dict(success=False))
        return


class Delete(RequestHandler):
    @tornado.web.authenticated
    def get(self):
        key = self.get_args('key', '')
        if key:
            result = self.redis.delete(key)

            self.write(dict(success=result))
            return

        self.write(dict(success=False))
        return


class Login(RequestHandler):
    def get(self):
        self.title = self._("Login")
        form = self.forms.LoginForm()
        self.render('login.html', form=form)

    def post(self):
        form = self.forms.LoginForm(self.request.arguments)

        if form.validate():
            if self.settings['username'] == form.username.data and \
                            self.settings['password'] == form.password.data:

                self.session['user'] = {'username': self.settings['username']}
                self.session.save()

                return self.redirect(self.reverse_url('index'))
            else:
                form.submit.errors.append(self._("The username or password you provided are incorrect."))

        self.render('login.html', form=form)


class Logout(RequestHandler):
    def get(self):
        del self.session['user']
        self.session.save()

        self.redirect(self.reverse_url('index'))
