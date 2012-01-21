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
from google.appengine.api import users


#error state decoder: 0 = no error, 1 = must enter name, 2 = name already taken, 3 = no recipe name entered
#4= incorrect format for cookbook name

class Cookbook(db.Model):
	user = db.UserProperty(required = True)
	author = db.StringProperty(required = False)
	name = db.StringProperty(required = True)
	#the difference b/t the name and the key name is that key name replaces the whitespaces with dashes
	date = db.DateTimeProperty(auto_now_add = True)

#defines single model for program, a recipe has content, author, date
class Recipe(db.Model):
	title = db.StringProperty(required = True)
	content = db.StringProperty(multiline = True) #required = True ?
	date = db.DateTimeProperty(auto_now_add = True)
	
#handler for the main page, renders opening template and creates a recipe object when post is clicked
class MainPage(webapp.RequestHandler):
	def get(self):	
		#you must be signed in to use!
		if users.get_current_user():
			error_state = 0
			no_errors = True
			values = {'error_state': error_state, 'no_errors': no_errors}
			self.response.out.write(template.render("main.html", values))
		else:
			self.redirect(users.create_login_url(self.request.uri))
			
	def post(self):	
		#a cookbook must have a name since that's how we identify it
		if bool(self.request.get('cookbookName')) == False:
			error_state = 1
			no_errors = False
			values = {'error_state': error_state, 'no_errors': no_errors}
			self.response.out.write(template.render("main.html", values))
			
		#a cookbook name can contain only letters, digits, and underscores (aka a regex word!)
		elif re.match("[\w\s]+$", self.request.get('cookbookName')) == None:
			error_state = 4
			no_errors = False
			values = {'error_state': error_state, 'no_errors': no_errors}
			self.response.out.write(template.render("main.html", values))
				
		else:
			#the cookbook key is constructed out of its name, except replacing whitespace w/dashes for URL purposes
			cookbook_key = self.request.get('cookbookName').strip().replace(' ', '-')
			#if no cookbook with this id exists make new cookbook, with the FORMATTED name (no whitespace!) as its key
				
			if Cookbook.get_by_key_name(cookbook_key) == None:
				new_cookbook = Cookbook(key_name = cookbook_key, user = users.get_current_user(), author = self.request.get('author'), name = self.request.get('cookbookName'))
				new_cookbook.put()
				self.redirect('/' + cookbook_key)
			
			#else show error message
			else:
				error_state = 2
				no_errors = False
				values = {'error_state': error_state, 'no_errors': no_errors}
				self.response.out.write(template.render("main.html", values))

			
#handler for cookbook page--searches all recipes and orders by date, then finds all the recipes with the correct cookbook key 	
class CookbookPageHandler(webapp.RequestHandler):
	
	def get(self, id):
		cookbook_key = id
		myCookbook = Cookbook.get_by_key_name(cookbook_key)		
		recipe_query = Recipe.all().ancestor(myCookbook).order('-date')
		recipes = []
		for item in recipe_query:
			recipes.append(item)		
			
		#check if the viewer is the author
		current_user = users.get_current_user()
		if current_user == myCookbook.user:
			is_author = True
		else:
			is_author = False
			
		#create logout link
		if users.get_current_user():
			logout_url = users.create_logout_url(self.request.uri)	
			loggedIn = True
			
		else:
			logout_url = ""
			loggedIn = False
			
		values = {'myCookbook': myCookbook, 'recipes' : recipes, 'is_author' : is_author, 'logout_url' : logout_url, 'loggedIn' : loggedIn}
		self.response.out.write(template.render("cookbook.html", values))
		
	def post(self, id):
		if bool(self.request.get('title')) == False:
			error_state = 3
			cookbook_key = id
			myCookbook = Cookbook.get_by_key_name(cookbook_key)
			recipe_query = Recipe.all().ancestor(myCookbook).order('-date')
			recipes = []
			for item in recipe_query:
				recipes.append(item)		
		
			#check if the viewer is the author
			current_user = users.get_current_user()
			if current_user == myCookbook.user:
				is_author = True
			else:
				is_author = False
			
			#create logout link
			if users.get_current_user():
				logout_url = users.create_logout_url(self.request.uri)		
				loggedIn = True
			
			else:
				logout_url = ""
				loggedIn = False
			
			
			values = {'recipes' : recipes, 'error_state': error_state, 'is_author': is_author, 'logout_url' : logout_url, 'loggedIn' : loggedIn}
			self.response.out.write(template.render("cookbook.html", values))
		
		else:
			error_state = 0
			cookbook_key = id
			myCookbook = Cookbook.get_by_key_name(cookbook_key)
			new_recipe = Recipe(parent = myCookbook, title = self.request.get('title'), content = self.request.get('content'))
			new_recipe.put()
			
			recipe_query = Recipe.all().ancestor(myCookbook).order('-date')
			recipes = []
			for item in recipe_query:
				recipes.append(item)		
				
			#check if the viewer is the author
			current_user = users.get_current_user()
			if current_user == myCookbook.user:
				is_author = True
			else:
				is_author = False
				
			#create logout link
			if users.get_current_user():
				logout_url = users.create_logout_url(self.request.uri)		
				loggedIn = True
			
			else:
				logout_url = ""
				loggedIn = False
			
			values = {'recipes' : recipes, 'error_state': error_state, 'is_author': is_author, 'logout_url' : logout_url, 'loggedIn': loggedIn}
			self.response.out.write(template.render("cookbook.html", values))
			
		self.redirect('/' + id)

	
class RecipeHandler(webapp.RequestHandler):
	def get(self, id):
		cookbook_key = id
		myCookbook = Cookbook.get_by_key_name(cookbook_key)
		recipe_query = Recipe.all().ancestor(myCookbook).order('-date')
		recipes = []
		for item in recipe_query:
			recipes.append(item)		
		self.response.out.write(template.render("chatscreen.html", {'recipes':recipes}))

class DeleteHandler(webapp.RequestHandler):
#needs to handle exceptions...

    def get(self, cookbook_id, recipe_name):
   		cookbook_key = cookbook_id
		myCookbook = Cookbook.get_by_key_name(cookbook_key)
		my_recipe = Recipe.all().ancestor(myCookbook).filter('title = ', recipe_name).get()
		my_recipe.delete()		 
		self.redirect('/' + cookbook_key)
    
def main():
	app = webapp.WSGIApplication([(r'/$', MainPage), (r'/mess/(\w*?)', RecipeHandler), (r'/([\w\-]+?)', CookbookPageHandler), (r'/delete/([\w\-]+?)/(.*?)', DeleteHandler)], debug=True)
	wsgiref.handlers.CGIHandler().run(app)

#implements program
if __name__ == "__main__":
	main()
	
	
	
	
	
	
	