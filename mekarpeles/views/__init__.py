#!/usr/bin/env python
# -*-coding: utf-8 -*-

"""
    __init__.py
    ~~~~~~~~~~~
    views

    :copyright: (c) 2015 by Mek Karpeles
    :license: see LICENSE for more details.
"""

import json
from flask import render_template, Response
from flask.views import MethodView
from werkzeug import wrappers
from configs import approot

class Base(MethodView):
    def get(self, uri=None):
        return render_template('base.html', template='index.html')

class Partial(MethodView):
    def get(self, partial):
        return render_template('partials/%s.html' % partial)

class Section(MethodView):
    def get(self, resource=None):
        layout = resource.replace(".html", "")
        if not resource or resource[-1] == '/':
            layout = resource + "index"
        try:
            return render_template("%s" % layout)
        except:
            return render_template('base.html', template='%s/index.html' % layout)


def rest_api(f):
    """Decorator to allow routes to return json"""
    def inner(*args, **kwargs):
        try:
            try:
                res = f(*args, **kwargs)
                if isinstance(res, wrappers.Response):
                    return res
                response = Response(json.dumps(res))
            except Exception as e:
                response = Response(json.dumps(e.__dict__))

            response.headers.add('Content-Type', 'application/json')
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            return response
        finally:
            #DB Rollbacks to protect against inconsistent states
            pass
    return inner

class Api(MethodView):
    @rest_api
    def get(self, resource=None):
        path = '%s/static/data/%s.json' % (approot, resource)
        with open(path) as f:
            return json.load(f)

