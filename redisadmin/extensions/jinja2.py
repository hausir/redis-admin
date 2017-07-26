# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import jinja2

from tornado_jinja2 import Jinja2Loader


def field_errors(field):
    """给静态文件添加修改时间"""

    template = jinja2.Template("""
        {% if field.errors %}
            <ul class="errors">
                {% for error in field.errors %}
                    <li>{{ error }}</li>
                {% endfor %}
            </ul>
        {% endif %}
        """)
    return template.render(field=field)

enviroment = jinja2.Environment(loader=jinja2.FileSystemLoader('redisadmin/templates/'))
enviroment.filters['field_errors'] = field_errors
loader = Jinja2Loader(enviroment)
