#!/usr/bin/env python
# coding=utf-8
import tornado.locale

from wtforms_tornado import Form
from wtforms.validators import required
from wtforms.fields import StringField, PasswordField, SubmitField, HiddenField


def create_forms(locale):

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

    return FormWrapper
