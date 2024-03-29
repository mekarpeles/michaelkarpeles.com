#!/usr/bin/env python
# -*-coding: utf-8 -*-

"""
    __init__.py
    ~~~~~~~~~~~
    views

    :copyright: (c) 2015 by Mek Karpeles
    :license: see LICENSE for more details.
"""


import re
import os
import json
import requests
from flask import render_template, Response, redirect, jsonify, request, Markup
from flask.views import MethodView
from werkzeug import wrappers
from configs import approot

ESSAYS_DIR = os.getcwd() + '/templates/essays/'

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


class Happy(MethodView):
    def get(self):
        return Posts().get(slug='happy')

class Learning(MethodView):
    def get(self):
        return Posts().get(slug='learning')

def get_post(slug):
    url = "https://graph.global/v1/posts?action=search&field=slug&query=%s&exact=true&limit=1&verbose=1"
    posts = requests.get(url % slug, verify=False).json()
    if posts['posts']:
        return posts['posts'][0]


class Posts(MethodView):
    def get(self, slug=None):
        if not slug:
            return jsonify(requests.get('https://graph.global/v1/posts', verify=False).json())
        url = "https://graph.global/v1/posts?action=search&field=slug&query=%s&exact=true&limit=1&verbose=1"
        results = requests.get(url % slug, verify=False).json()

        def tagify(text):
            return Markup(
                re.sub('\[{2}([0-9]+)\:([^\]]+)\]{2}',
                       '<cite w2gid="\g<1>">\g<2></cite>', text))

        post = get_post(slug)
        if post:
            title = post.get('title')
            body  = post.get('post')
            tagmap = dict(re.findall('\[\[([0-9]+):([^\]]*)\]', title + body))
            md = ''.join(['<p>%s</p>' % p for p in body.split('<br>') if p])
            tags  = ', '.join(set(re.findall('(\[{2}[^\]]+\]{2})', title + body)))
            related_posts = post.get('related_posts', [])
            for i, rp in enumerate(related_posts):
                related_posts[i]['related_tags'] = {}
                related_posts[i]['tags'] = dict(re.findall(
                        '\[\[([0-9]+):([^\]]*)\]',
                        related_posts[i]['title'] + related_posts[i]['post']))
                for tid, tval in related_posts[i]['tags'].items():
                    if tid in tagmap:
                        related_posts[i]['related_tags'][tid] = tval
                related_posts[i]['title'] = tagify(related_posts[i]['title'])

            return render_template('base.html', template='post.html', post=post,
                                   tags=tagify(tags), title=tagify(title), body=tagify(body),
                                   related_posts=related_posts)
        

class Edit(MethodView):
    def get(self, slug=''):
        post = slug and get_post(slug)
        if post:
            post['post'] = Markup(post['post'])
        return render_template('base.html', template='edit.html', post=post, slug=slug)


class Base(MethodView):
    def get(self, uri=None):
        try:
            return render_template('base.html', template='index.html')
        except:
            return redirect('/')


class Verbatim(MethodView):
    def get(self):
        try:
            return render_template('%s.html' % request.path)
        except Exception as e:
            return redirect('/')


class Projects(MethodView):
    def get(self):
        return redirect('https://docs.google.com/document/d/e/2PACX-1vTlJig0XEdoAIcK-FjzJvoFcSz1mnPKcOm0Sb1HdAwRP-xCuWXqKlFpWTb04HgcwDJ0vupplJgcQoM6/pub')

class Partial(MethodView):
    def get(self, partial):
        return render_template('partials/%s.html' % partial)


class Section(MethodView):
    def get(self, resource=None):
        layout = resource#.replace(".html", "")
        if not resource or resource[-1] == '/':
            layout = resource + "index"
        try:
            return render_template('base.html', template="%s.html" % layout)
        except:            
            return render_template('base.html', template='%s/index.html' % layout)


class Api(MethodView):
    @rest_api
    def get(self, resource=None):
        path = '%s/static/data/%s.json' % (approot, resource)
        with open(path) as f:
            return json.load(f)


class QSApi(MethodView):

    def get(self):
        uri = "https://spreadsheets.google.com/feeds/list"
        sid = "1k-zl-Ya4OAU7Lp8DsPGy7mSJVCeXSPqK673Wiq8ndt8"
        gid = "oauobz3"
        url = "%s/%s/%s/public/values?alt=json" % (uri, sid, gid)
        return jsonify(requests.get(url).json())

class QS(MethodView):

    def get(self):
        return redirect('https://docs.google.com/spreadsheets/d/1k-zl-Ya4OAU7Lp8DsPGy7mSJVCeXSPqK673Wiq8ndt8')

class ASD(MethodView):

    def get(self, year="2020"):        
        return redirect('https://tinyurl.com/mek-asd-' + year)

class HOPE(MethodView):

    def get(self):
        return redirect('https://docs.google.com/presentation/d/e/2PACX-1vTrSo8hSwXq8f7lVwrbo6i7bAd2pF3Be1k8RrJYDIb8hCmmYHTTPNbOMdAAbf7XkF2_NPFTA3KSaK4X/pub?start=false')
