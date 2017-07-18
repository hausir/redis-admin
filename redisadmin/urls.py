# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from tornado.web import url
from redisadmin.views.base import ErrorHandler
from redisadmin.views.frontend import (
    Index,
    Connection,
    Menu,
    New,
    Value,
    List,
    Info,
    FlushDB,
    FlushAll,
    Expire,
    Move,
    Edit,
    Add,
    Remove,
    Pop,
    Delete,
    Login,
    Logout
)


url_patterns = [
    url(r"/", Index, name='index'),
    url(r"/connection", Connection, name='connection'),
    url(r"/menu", Menu, name='menu'),
    url(r"/new", New, name='new'),
    url(r"/value", Value, name='value'),
    url(r"/list", List, name='list'),
    url(r"/info", Info, name='info'),
    url(r"/flush/db", FlushDB, name='flush_db'),
    url(r"/flush/all", FlushAll, name='flush_all'),
    url(r"/expire", Expire, name='expire'),
    url(r"/move", Move, name='move'),
    url(r"/edit", Edit, name='edit'),
    url(r"/add", Add, name='add'),
    url(r"/remove", Remove, name='remove'),
    url(r"/pop", Pop, name='pop'),
    url(r"/delete", Delete, name='delete'),
    url(r"/login", Login, name='login'),
    url(r"/logout", Logout, name='logout'),
    url(r"/(.*)", ErrorHandler),
]
