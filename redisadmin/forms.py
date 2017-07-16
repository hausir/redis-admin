#!/usr/bin/env python
# coding=utf-8
import tornado.locale

from wtforms.fields import StringField, PasswordField, SubmitField, HiddenField
from redisadmin.extensions.forms import Form, required


def create_forms():
    _forms = {}

    for locale in tornado.locale.get_supported_locales():
        translate = tornado.locale.get(locale).translate

        class FormWrapper(object):
            class LoginForm(Form):
                username = StringField(
                    translate("Username"),
                    validators=[
                        required(
                            message=translate("You must provide an username")
                        )
                    ]
                )

                password = PasswordField(translate("Password"))

                next = HiddenField()

                submit = SubmitField(translate("Login"))

        _forms[locale] = FormWrapper

    return _forms
