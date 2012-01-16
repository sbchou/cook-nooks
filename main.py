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
	#you can leave author blank if you must, cookbooks are ID'd by name
	author = db.StringProperty(required = False)
	name = db.StringProperty(required = True)
	date = db.DateTimeProperty(auto_now_add = True)
	#fix this
	cookbook_id = db.StringProperty(required = True)

#defines single model for program, a recipe has content, author, cookbook_id , date
class Recipe(db.Model):
	title = db.StringProperty(required = True)
	content = db.StringProperty(multiline = True) #required = True ?
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
		random_id = str(random.randint(1000000000, 9999999999))
		
		#a cookbook must have a name since that's how we identify it
		if bool(self.request.get('cookbookName')) == False:
			error_state = True
			no_errors = False
			values = {'error_state': error_state, 'no_errors': no_errors}
			self.response.out.write(template.render("main.html", values))
			
		else:
			#create a new cookbook
			cookbook_name = self.request.get('cookbookName')
			new_cookbook = Cookbook(author = self.request.get('author'), name = cookbook_name, cookbook_id = random_id)
			new_cookbook.put()
			self.redirect('/' + random_id)


#handler for cookbook page--searches all recipes and orders by date, then finds all the recipes with the correct cookbook_id 	
class CookbookPageHandler(webapp.RequestHandler):
	
	def get(self, id):
		cookbook_query = Cookbook.all().filter('cookbook_id =', id)
		myCookbook = cookbook_query.get()
		recipe_query = Recipe.all().ancestor(myCookbook).order('-date')
		recipes = []
		for item in recipe_query:
			recipes.append(item)		
		values = {'myCookbook': myCookbook, 'recipes' : recipes}
		self.response.out.write(template.render("cookbook.html", values))
		
	def post(self, id):
		if bool(self.request.get('title')) == False:
			#person = self.request.get('author')
			cookbook_query = Cookbook.all().filter('cookbook_id =', id)
			myCookbook = cookbook_query.get()
			recipe_query = Recipe.all().ancestor(myCookbook).order('-date')
			recipes = []
			for item in recipe_query:
				recipes.append(item)		
			error_state = True
			values = {'recipes' : recipes, 'error_state': error_state}
			self.response.out.write(template.render("cookbook.html", values))
		else:
			cookbook_query = Cookbook.all().filter('cookbook_id =', id)
			myCookbook = cookbook_query.get()
			new_recipe = Recipe(parent = myCookbook, title = self.request.get('title'), content = self.request.get('content'))
			new_recipe.put()
			
			recipe_query = Recipe.all().ancestor(myCookbook).order('-date')
			recipes = []
			for item in recipe_query:
				recipes.append(item)		
				
			error_state = False
			values = {'recipes' : recipes, 'error_state': error_state}
			self.response.out.write(template.render("cookbook.html", values))
		
class RecipeHandler(webapp.RequestHandler):
	def get(self, id):
		cookbook_query = Cookbook.all().filter('cookbook_id =', id)
		myCookbook = cookbook_query.get()
		recipe_query = Recipe.all().ancestor(myCookbook).order('-date')
		recipes = []
		for item in recipe_query:
			recipes.append(item)		
		self.response.out.write(template.render("chatscreen.html", {'recipes':recipes}))

def main():
	app = webapp.WSGIApplication([
		(r'/$', MainPage), (r'/mess/(\w*)', RecipeHandler), (r'/(\d*)', CookbookPageHandler)], debug=True)
	wsgiref.handlers.CGIHandler().run(app)

#implements program
if __name__ == "__main__":
	main()