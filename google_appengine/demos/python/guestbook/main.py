#!/usr/bin/env python
#
# Copyright 2007 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

















"""Guestbook inspired app for testing python3 api access."""
import datetime
import os
from urllib import parse
import flask
from flask import Flask
import google.appengine.api
from google.appengine.api import memcache
from google.appengine.api import urlfetch
from google.appengine.api import users
from google.appengine.ext import ndb
import jinja2


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    autoescape=True)



DEFAULT_GUESTBOOK_NAME = 'default_guestbook'


app = Flask(__name__)
app.wsgi_app = google.appengine.api.wrap_wsgi_app(app.wsgi_app)







def guestbook_key(guestbook_name=DEFAULT_GUESTBOOK_NAME):
  """Constructs a Datastore key for a Guestbook entity."""
  return ndb.Key('Guestbook', guestbook_name)



class Author(ndb.Model):
  """Sub model for representing an author."""
  identity = ndb.StringProperty(indexed=False)
  email = ndb.StringProperty(indexed=False)


class Greeting(ndb.Model):
  """A main model for representing an individual Guestbook entry."""
  author = ndb.StructuredProperty(Author)
  content = ndb.StringProperty(indexed=False)
  date = ndb.DateTimeProperty(auto_now_add=True)





@app.route('/', methods=['GET'])
def get():
  """Handle GET."""
  guestbook_name = flask.request.args.get('guestbook_name',
                                          DEFAULT_GUESTBOOK_NAME)
  greetings_query = Greeting.query(
      ancestor=guestbook_key(guestbook_name)).order(-Greeting.date)
  greetings = greetings_query.fetch(10)

  user = users.get_current_user()
  if user:
    url = users.create_logout_url(flask.request.url)
    url_linktext = 'Logout'
  else:
    url = users.create_login_url(flask.request.url)
    url_linktext = 'Login'

  template_values = {
      'user': user,
      'greetings': greetings,
      'guestbook_name': parse.quote(guestbook_name),
      'url': url,
      'url_linktext': url_linktext,
      'lasttime': memcache.get('lasttime')
  }

  template = JINJA_ENVIRONMENT.get_template('index.html')
  return template.render(template_values)


@app.route('/sign', methods=['POST'])
def post():
  """Handle post."""





  guestbook_name = flask.request.args.get('guestbook_name',
                                          DEFAULT_GUESTBOOK_NAME)
  greeting = Greeting(parent=guestbook_key(guestbook_name))

  if users.get_current_user():
    greeting.author = Author(
        identity=users.get_current_user().user_id(),
        email=users.get_current_user().email())

  greeting_url = str(flask.request.form.get('content')).strip()
  greeting.content = str(urlfetch.fetch(greeting_url).content[:100])
  greeting.put()
  memcache.set('lasttime', str(datetime.datetime.now()))

  query_params = {'guestbook_name': guestbook_name}
  return flask.redirect('/?' + parse.urlencode(query_params))
