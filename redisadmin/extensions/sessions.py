# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import json
import redis

from uuid import uuid4
from redisadmin.settings import settings


class RedisSession(object):
    def __init__(self, session_id=None, expires=None):
        self.redis = redis.StrictRedis(
            host=settings.get('redis_host'),
            port=settings.get('redis_port'),
            password=settings.get('redis_password'),
            db=0, decode_responses=True
        )
        self._sid = session_id if session_id else uuid4().hex
        self._key = 'session:{}'.format(self._sid)
        self._data = self.get_session('data')
        self._expires = expires
        self._dirty = False

    def clear(self):
        self.redis.delete(self._key)

    @property
    def id(self):
        return self._sid

    def __getitem__(self, key):
        return self._data.get(key)

    def __setitem__(self, key, value):
        self._data[key] = value
        self._dirty = True

    def __delitem__(self, key):
        del self._data[key]
        self._dirty = True

    def __len__(self):
        return len(self._data)

    def __contains__(self, key):
        return key in self._data

    def __iter__(self):
        for key in self._data:
            yield key

    def __repr__(self):
        return self._data.__repr__()

    def __del__(self):
        self.save()

    def save(self):
        if self._dirty:
            self.set_session(self._data, 'data', self._expires)
            self._dirty = False

    def get_session(self, name):
        data = self.redis.hget(self._key, name)
        session = json.loads(data) if data else dict()
        return session

    def set_session(self, session_data, name, expiry=None):
        self.redis.hset(self._key, name, json.dumps(session_data))
        expiry = expiry or self.options['expire']
        if expiry:
            self.redis.expire(self._key, expiry)
