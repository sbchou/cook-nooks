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
    cookbook = db.StringProperty(required = True)

class MainPage(webapp.RequestHandler):
	def get(self):
		error_state = False
		no_errors = True
		values = {'error_state': error_state, 'no_errors': no_errors}
		self.response.out.write(template.render("main.html", values))
	
	def post(self):
		resource_name = str(random.randint(1000000000, 9999999999))
		if bool(self.request.get('message')) == False:
			error_state = True
			no_errors = False
			values = {'error_state': error_state, 'no_errors': no_errors}
			self.response.out.write(template.render("main.html", values))
        
		else:
			new_post = Post(message = self.request.get('message'), who = self.request.get('who'), discussion_id = resource_name)
			new_post.put()
			self.re
  

class Cookbook(webapp2.RequestHandler):
    def get(self):
        cookbook_name=self.request.get('cookbook_name')
        recipes_query = Recipe.all().order('-date')
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
        cookbook_name = self.request.get('cookbook_name')
        recipe = Recipe(parent=cookbook_key(cookbook_name))

        if users.get_current_user():
            recipe.author = users.get_current_user()

        recipe.content = self.request.get('content')
        recipe.put()
        self.redirect('/?' + urllib.urlencode({'cookbook_name': cookbook_name}))


app = webapp2.WSGIApplication([('/', Cookbook),
                               ('/sign', Cookbook)],
                              debug=True)