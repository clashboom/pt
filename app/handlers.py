#!/usr/bin/env python
# encoding: utf-8

import jinja2
import os
import webapp2
import logging

# from google.appengine.api import memcache
from webapp2_extras import sessions
from webapp2_extras import sessions_memcache

from django.utils import simplejson

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')
JINJA_ENV = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE_DIR),
                               autoescape=True)


class NotFound(Exception):
    pass


class Forbidden(Exception):
    pass


class BadRequest(Exception):
    pass


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    @classmethod
    def render_str(cls, template, *a, **params):
        template = JINJA_ENV.get_template(template)
        return template.render(params)

    def render(self, template, locale=None, *a, **params):
        self.write(self.render_str(template, locale=locale, *a, **params))

    def reply(self, content, content_type='text/plain', status=200):
        self.response.headers['Content-Type'] = content_type + '; charset=utf-8'
        self.write(content)

    def dump_request(self):
        for k in self.request.argments():
            logging.debug('%s = %s' % (k, self.request.get(k)))

    def handle_exception(self, e, debug_mode):
        if debug_mode or True:
            logging.error(e, exc_info=True)

        if self.is_ajax():
            self.reply(simplejson.dumps({
                "status": "error",
                "error": unicode(e),
                "error_class": e.__class__.__name__,
            }), "application/json")
        elif type(e) == BadRequest:
            self.show_error_page(400)
        elif type(e) == Forbidden:
            self.show_error_page(403)
        elif type(e) == NotFound:
            self.show_error_page(404)
        elif debug_mode:
            return webapp2.RequestHandler.handle_exception(self, e, debug_mode)
        else:
            self.show_error_page(500)

    def redirect(self, url):
        if self.is_ajax():
            return self.reply(simplejson.dumps({
                "status": "redirect",
                "url": url,
            }))
        return super(webapp2.RequestHandler, self).redirect(url)

    def is_ajax(self):
        return os.environ.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest"

    def dispatch(self):
        self.session_store = sessions.get_store(request=self.request)
        try:
            webapp2.RequestHandler.dispatch(self)
        finally:
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        return self.session_store.get_session(name='pt_session',
                                              factory=sessions_memcache.
                                              MemcacheSessionFactory)


class HomeHandler(Handler):
    def get(self):
        self.render("index.html")


class OrderHandler(Handler):
    def get(self):
        self.render("orders.html")


# Webapp2 config
config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': 'navettes-not-so-secret-key',
    'name': 'navette_session',
}


app = webapp2.WSGIApplication([
    ('/orders', OrderHandler),
    ('.*', HomeHandler),
], config=config, debug=True)
