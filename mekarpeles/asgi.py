#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
asgi.py — FastAPI (Python 3) port of the michaelkarpeles.com / mek.fyi app.

Faithful re-implementation of the original Flask (Py2) app in mekarpeles/app.py:
  - Most of the site is Jinja templates rendered by path via base.html (Section/Base).
  - A few API/proxy/redirect routes.
  - /posts, /rss, /edit are backed by the external https://graph.global/v1/posts API.

Run:  uvicorn mekarpeles.asgi:app --host 127.0.0.1 --port 8080
(nginx proxies to it and serves /static; see deploy/ in this branch.)
"""
import os
import re
import json
import urllib3
import requests
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from markupsafe import Markup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(HERE, "templates")
STATIC_DIR = os.path.join(HERE, "static")
DATA_DIR = os.path.join(STATIC_DIR, "data")
GRAPH_POSTS = "https://graph.global/v1/posts"

app = FastAPI(title="michaelkarpeles.com")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# The original app ran under Flask, which provided url_for/request globals. One essay
# template references url_for in example markup; shim it so rendering never crashes.
templates.env.globals["url_for"] = lambda *a, **k: "#"


def titler(path):
    title = path.split("/")[-1].rsplit(".", 1)[0]
    if title == "index" or not title.strip():
        title = "Home"
    return title.replace("-", " ").capitalize()


def render(request, inner, status_code=200, **ctx):
    """Render base.html, including the inner template (mirrors the Flask base.html pattern)."""
    ctx["template"] = inner
    ctx["titler"] = lambda: titler(request.url.path)
    return templates.TemplateResponse(request=request, name="base.html",
                                      context=ctx, status_code=status_code)


# ---------------------------------------------------------------------------
# graph.global-backed posts/rss/edit
# ---------------------------------------------------------------------------
def get_post(slug):
    url = GRAPH_POSTS + "?action=search&field=slug&query=%s&exact=true&limit=1&verbose=1"
    posts = requests.get(url % slug, verify=False, timeout=15).json()
    return posts["posts"][0] if posts.get("posts") else None


def tagify(text):
    return Markup(re.sub(r'\[{2}([0-9]+)\:([^\]]+)\]{2}',
                         r'<cite w2gid="\g<1>">\g<2></cite>', text or ""))


def _escape_html(text):
    return (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;").replace("'", "&apos;"))


def _format_pub_date(date_str):
    try:
        return datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %Z").strftime('%a, %d %b %Y %H:%M:%S %z')
    except Exception:
        return date_str


def convert_to_rss(json_data):
    rss = Element('rss', attrib={'version': '2.0'})
    channel = SubElement(rss, 'channel')
    SubElement(channel, 'title').text = "Mek's Blog"
    SubElement(channel, 'link').text = 'https://mek.fyi'
    SubElement(channel, 'description').text = 'Thinking out loudly'
    for post in json_data.get('posts', []):
        item = SubElement(channel, 'item')
        SubElement(item, 'title').text = post.get('title', '')
        SubElement(item, 'link').text = 'https://mek.fyi/posts/%s' % post.get("slug", "")
        SubElement(item, 'description').text = _escape_html((post.get('post') or '')[:100] + "...")
        SubElement(item, 'pubDate').text = _format_pub_date(post.get('created', ''))
        guid = SubElement(item, 'guid', attrib={'isPermaLink': 'false'})
        guid.text = 'https://mek.fyi/posts/%s' % post.get("slug", "")
    return minidom.parseString(tostring(rss)).toprettyxml(indent="    ")


# ---------------------------------------------------------------------------
# routes  (specific first; the catch-all Section MUST stay last)
# ---------------------------------------------------------------------------
@app.get("/")
def home(request: Request):
    return render(request, "index.html")


@app.get("/rss")
def rss():
    data = requests.get(GRAPH_POSTS, verify=False, timeout=15).json()
    return Response(convert_to_rss(data), media_type="application/rss+xml")


@app.get("/posts")
def posts_index():
    return JSONResponse(requests.get(GRAPH_POSTS, verify=False, timeout=15).json())


@app.get("/posts/{slug:path}")
def posts_show(request: Request, slug: str):
    post = get_post(slug)
    if not post:
        return RedirectResponse("/")
    title = post.get("title") or ""
    body = post.get("post") or ""
    tagmap = dict(re.findall(r'\[\[([0-9]+):([^\]]*)\]', title + body))
    tags = ', '.join(set(re.findall(r'(\[{2}[^\]]+\]{2})', title + body)))
    related = post.get("related_posts", []) or []
    for rp in related:
        rp["related_tags"] = {}
        rp["tags"] = dict(re.findall(r'\[\[([0-9]+):([^\]]*)\]',
                                     (rp.get("title") or "") + (rp.get("post") or "")))
        for tid, tval in rp["tags"].items():
            if tid in tagmap:
                rp["related_tags"][tid] = tval
        rp["title"] = tagify(rp.get("title"))
    return render(request, "post.html", post=post, tags=tagify(tags),
                  title=tagify(title), body=tagify(body), related_posts=related)


@app.get("/edit")
@app.get("/edit/{slug:path}")
def edit(request: Request, slug: str = ""):
    post = get_post(slug) if slug else None
    if post:
        post["post"] = Markup(post["post"])
    return render(request, "edit.html", post=post, slug=slug)


@app.get("/happy")
def happy(request: Request):
    return posts_show(request, "happy")


@app.get("/learning")
def learning(request: Request):
    return posts_show(request, "learning")


# verbatim pages (original rendered the template at the request path directly)
@app.get("/math")
@app.get("/genealogy")
def verbatim(request: Request):
    name = request.url.path.strip("/") + ".html"
    if os.path.isfile(os.path.join(TEMPLATES_DIR, name)):
        return templates.TemplateResponse(
            request=request, name=name,
            context={"titler": lambda: titler(request.url.path)})
    return RedirectResponse("/")


# redirects
@app.get("/table-of-projects")
def table_of_projects():
    return RedirectResponse("https://docs.google.com/document/d/e/2PACX-1vTlJig0XEdoAIcK-FjzJvoFcSz1mnPKcOm0Sb1HdAwRP-xCuWXqKlFpWTb04HgcwDJ0vupplJgcQoM6/pub")


@app.get("/qs")
def qs():
    return RedirectResponse("https://docs.google.com/spreadsheets/d/1k-zl-Ya4OAU7Lp8DsPGy7mSJVCeXSPqK673Wiq8ndt8")


@app.get("/hope")
def hope():
    return RedirectResponse("https://docs.google.com/presentation/d/e/2PACX-1vTrSo8hSwXq8f7lVwrbo6i7bAd2pF3Be1k8RrJYDIb8hCmmYHTTPNbOMdAAbf7XkF2_NPFTA3KSaK4X/pub?start=false")


@app.get("/asd{year:path}")
def asd(year: str = "2020"):
    return RedirectResponse("https://tinyurl.com/mek-asd-" + (year or "2020"))


# api: quantified-self proxy (must precede the generic data api)
@app.get("/api/v1/quantified-self")
def qs_api():
    url = ("https://spreadsheets.google.com/feeds/list/"
           "1k-zl-Ya4OAU7Lp8DsPGy7mSJVCeXSPqK673Wiq8ndt8/oauobz3/public/values?alt=json")
    return JSONResponse(requests.get(url, timeout=15).json())


# api: serve static/data/<resource>.json
@app.get("/api/v1/{resource:path}")
def data_api(resource: str):
    path = os.path.join(DATA_DIR, resource + ".json")
    try:
        with open(path) as f:
            return JSONResponse(json.load(f),
                                headers={"Access-Control-Allow-Credentials": "true"})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=404)


# static files (mounted before the catch-all so /static wins)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# catch-all: render any template by path (Section). KEEP LAST.
@app.get("/{resource:path}")
def section(request: Request, resource: str):
    layout = resource
    if not resource or resource.endswith("/"):
        layout = resource + "index"
    for candidate in ("%s.html" % layout, "%s/index.html" % layout):
        if os.path.isfile(os.path.join(TEMPLATES_DIR, candidate)):
            return render(request, candidate)
    return RedirectResponse("/")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)
