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

#defines single model for program, a post has content, author, discussion_id , date
class Post(db.Model):
	content = db.StringProperty(required = False)
	author = db.StringProperty(required = False)
	discussion_id  = db.StringProperty(required = True)
	date = db.DateTimeProperty(auto_now_add = True)
	
#handler for the main page, renders opening template and creates a post object when post is clicked
class MainPage(webapp.RequestHandler):
	def get(self):
		error_state = False
		no_errors = True
		values = {'error_state': error_state, 'no_errors': no_errors}
		self.response.out.write(template.render("main.html", values))
	
	def post(self):
		cookbook_name = str(random.randint(1000000000, 9999999999))
		if bool(self.request.get('content')) == False:
			error_state = True
			no_errors = False
			values = {'error_state': error_state, 'no_errors': no_errors}
			self.response.out.write(template.render("main.html", values))
			
		else:
			new_post = Post(content = self.request.get('content'), author = self.request.get('author'), discussion_id  = cookbook_name)
			new_post.put()
			self.redirect('/' + cookbook_name)


#handler for discussion page--searches all posts and orders by date, then finds all the posts with the correct discussion_id 	
class DiscussionPageHandler(webapp.RequestHandler):
	
	def get(self, id):
		query = GqlQuery("SELECT *FROM Post ORDER BY date ASC")
		posts = []
		for item in query:
			if item.discussion_id  == id:
				posts.append(item)
		values = {'posts' : posts}
		self.response.out.write(template.render("discussion.html", values))
		
	def post(self, id):
		if bool(self.request.get('content')) == False:
			person = self.request.get('author')
			query = GqlQuery("SELECT *FROM Post ORDER BY date ASC")
			posts = []
			for item in query:
				if item.discussion_id  == id:
					posts.append(item)
			error_state = True
			values = {'posts' : posts, 'person': person, 'error_state': error_state}
			self.response.out.write(template.render("discussion.html", values))
		else:
			new_post = Post(content = self.request.get('content'), author = self.request.get('author'), discussion_id  = id)
			new_post.put()
			person = self.request.get('author')
			query = GqlQuery("SELECT *FROM Post ORDER BY date ASC")
			posts = []
			for item in query:
				if item.discussion_id  == id:
					posts.append(item)
			error_state = False
			values = {'posts' : posts, 'person': person, 'error_state': error_state}
			self.response.out.write(template.render("discussion.html", values))
		
class MessageHandler(webapp.RequestHandler):
	def get(self, id):
		query = GqlQuery("SELECT *FROM Post ORDER BY date ASC")
		posts = []
		for item in query:
			if item.discussion_id  == id:
				posts.append(item)
		self.response.out.write(template.render("chatscreen.html", {'posts':posts}))

def main():
	app = webapp.WSGIApplication([
		(r'/$', MainPage), (r'/mess/(\w*)', MessageHandler), (r'/(\d*)', DiscussionPageHandler)], debug=True)
	wsgiref.handlers.CGIHandler().run(app)

#implements program
if __name__ == "__main__":
	main()