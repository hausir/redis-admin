# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals


class Pagination(object):
    def __init__(self, query, page, per_page):
        self.query = query
        self.per_page = per_page
        self.page = page

    @property
    def total(self):
        return len(self.query)

    @property
    def items(self):
        return self.query[(self.page - 1) * self.per_page: self.page * self.per_page]

    def iter_pages(self, left_edge=2, left_current=2,
                   right_current=5, right_edge=2):
        last = 0
        for num in range(1, self.pages + 1):
            if num <= left_edge or (self.page - left_current - 1 < num < self.page + right_current) or num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num

    has_prev = property(lambda x: x.page > 1)
    prev_num = property(lambda x: x.page - 1)
    has_next = property(lambda x: x.page < x.pages)
    next_num = property(lambda x: x.page + 1)
    pages = property(lambda x: max(0, x.total - 1) // x.per_page + 1)
