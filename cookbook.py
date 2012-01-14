import jinja2
import os

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

import cgi
import datetime
import urllib
import webapp2

from google.appengine.ext import db
from google.appengine.api import users


class Recipe(db.Model):
    """all your comments here"""
    author = db.UserProperty()
    content = db.StringProperty(multiline=True)
    date = db.DateTimeProperty(auto_now_add=True)
  


def guestbook_key(guestbook_name=None):
  """Constructs a datastore key for a Guestbook entity with guestbook_name."""
  return db.Key.from_path('Guestbook', guestbook_name or 'default_guestbook')    

class Guestbook(webapp2.RequestHandler):
    def get(self):
        guestbook_name=self.request.get('guestbook_name')
        recipes_query = Recipe.all().ancestor(
                                                  guestbook_key(guestbook_name)).order('-date')
        recipes = recipes_query.fetch(10)
        
        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
        
        template_values = {
            'recipes': recipes,
            'url': url,
            'url_linktext': url_linktext,
        }
        
        template = jinja_environment.get_template('index.html')
        self.response.out.write(template.render(template_values))
    
    
    def post(self):
        # We set the same parent key on the 'Greeting' to ensure each greeting is in
        # the same entity group. Queries across the single entity   group will be
        # consistent. However, the write rate to a single entity group should
        # be limited to ~1/second.
        guestbook_name = self.request.get('guestbook_name')
        recipe = Recipe(parent=guestbook_key(guestbook_name))

        if users.get_current_user():
            recipe.author = users.get_current_user()

        recipe.content = self.request.get('content')
        recipe.put()
        self.redirect('/?' + urllib.urlencode({'guestbook_name': guestbook_name}))


app = webapp2.WSGIApplication([('/', Guestbook),
                               ('/sign', Guestbook)],
                              debug=True)