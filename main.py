from google.appengine.ext import webapp
import wsgiref.handlers
from google.appengine.ext.webapp \
	import template
from google.appengine.ext import db
import os
import sys
import re
import random
from google.appengine.ext.db import GqlQuery


class Cookbook(db.Model):
	author = db.StringProperty(required = False)
	name = db.StringProperty(required = True)
	date = db.DateTimeProperty(auto_now_add = True)

#defines single model for program, a recipe has content, author, cookbook_id , date
class Recipe(db.Model):
	title = db.StringProperty(required = False)
	content = db.StringProperty(required = False)
	date = db.DateTimeProperty(auto_now_add = True)
	
#handler for the main page, renders opening template and creates a recipe object when post is clicked
class MainPage(webapp.RequestHandler):
	def get(self):
		error_state = False
		no_errors = True
		values = {'error_state': error_state, 'no_errors': no_errors}
		self.response.out.write(template.render("main.html", values))
	
	def post(self):
		#gotta fix this
		cookbook_name = str(random.randint(1000000000, 9999999999))
		
		#a cookbook must have a name since that's how we identify it
		if bool(self.request.get('cookbookName')) == False:
			error_state = True
			no_errors = False
			values = {'error_state': error_state, 'no_errors': no_errors}
			self.response.out.write(template.render("main.html", values))
			
		else:
			#create a new cookbook
			new_cookbook = Cookbook(author = self.request.get('author'), name = self.request.get('cookbookName'))
			new_cookbook.put()
			self.redirect('/' + cookbook_name)


#handler for cookbook page--searches all recipes and orders by date, then finds all the recipes with the correct cookbook_id 	
class CookbookPageHandler(webapp.RequestHandler):
	
	def get(self, id):
		query = Recipe.all().filter('cookbook_id =', id).order('-date')
		recipes = []
		for item in query:
			recipes.append(item)		
		values = {'recipes' : recipes}
		self.response.out.write(template.render("cookbook.html", values))
		
	def post(self, id):
		if bool(self.request.get('content')) == False:
			person = self.request.get('author')
			query = Recipe.all().filter('cookbook_id =', id).order('-date')
			recipes = []
			for item in query:
				recipes.append(item)		
			error_state = True
			values = {'recipes' : recipes, 'person': person, 'error_state': error_state}
			self.response.out.write(template.render("cookbook.html", values))
		else:
			new_recipe = Recipe(content = self.request.get('content'), author = self.request.get('author'), cookbook_id  = id)
			new_recipe.put()
			person = self.request.get('author')
			query = Recipe.all().filter('cookbook_id =', id).order('-date')
			recipes = []
			for item in query:
				recipes.append(item)		
			error_state = False
			values = {'recipes' : recipes, 'person': person, 'error_state': error_state}
			self.response.out.write(template.render("cookbook.html", values))
		
class RecipeHandler(webapp.RequestHandler):
	def get(self, id):
		query = Recipe.all().filter('cookbook_id =', id).order('-date')
		recipes = []
		for item in query:
			recipes.append(item)		
		self.response.out.write(template.render("chatscreen.html", {'recipes':recipes}))

def main():
	app = webapp.WSGIApplication([
		(r'/$', MainPage), (r'/mess/(\w*)', RecipeHandler), (r'/(\d*)', CookbookPageHandler)], debug=True)
	wsgiref.handlers.CGIHandler().run(app)

#implements program
if __name__ == "__main__":
	main()