import entities
from entities import db
import logging

import wutil # web utilties
import json
from handlers.base import AppHandler
from datetime import datetime, timedelta
import dataDelegate as dd 

PARAM_FOOD_TYPE = 'type' 
PARAM_FOOD_ID = 'foodID'
PARAM_OS_TYPE = 'ostype'
PARAM_USER_ID = 'userID'
PARAM_VOTE = 'vote'
PARAM_COMMENT = 'comment'

FOOD_MARKETPLACE = 'marketplace'
FOOD_SMOKEHOUSE  = 'smokehouse'



class SplashPage(AppHandler):
	def get(self):
		self.render("splashPage.html")

# Handler for a permalink address /[post_id]
class MainPage(AppHandler):

  def get(self):
	userHash = self.request.cookies.get(PARAM_USER_ID, None)
	if (userHash is None):
		os_type = self.request.headers["User-Agent"]
		# create a new anonymous user entity, give json response with hashed id
		new_user = entities.User(os_type = os_type)
		new_user.put()
		generated_hash = wutil.createSecret( new_user.key().id() )
		expires = datetime.now() + timedelta(days=1500)
		dead_date = expires.strftime('%a, %d-%b-%Y %H:%M:%S')
		self.response.headers.add_header('Set-Cookie', '%s=%s; Path=/; expires=%s;' % (PARAM_USER_ID, generated_hash, dead_date))

	# user should have an identifier
	foodType = self.request.get(PARAM_FOOD_TYPE)
	if foodType not in (FOOD_MARKETPLACE, FOOD_SMOKEHOUSE):
		foodType = FOOD_MARKETPLACE
	dataTuple = dd.fetchRatings(foodType)
	entry = dataTuple[0]

	entry_id = entry.key().id()
	# find if the user voted, and change vote arrows
	cookie = self.request.cookies.get(str(entry_id), None)
	up_selected = ""
	down_selected = ""
	if cookie is not None:
		if cookie == '1':
			up_selected = "_selected"
		if cookie == '0':
			down_selected = "_selected"


	if entry.totalVotes == 0:
		percentage = 0
	else:
		percentage = int((((float(entry.upvotes) / entry.totalVotes) * 100)))
	downvotes = entry.totalVotes - entry.upvotes

	voteComments = dataTuple[1]
	commentHTML = dd.generateCommentsHTML(voteComments)

	self.render("index.html", type_name=entry.name, percentage=percentage, 
							upvotes=entry.upvotes, downvotes=downvotes,
							entry_id = entry_id, up=up_selected, down=down_selected,
							comments=commentHTML)

class CommentPage(AppHandler):
	def get(self):
		# get param of the food_id, place it inside the form
		food_id = self.request.get("food")
		food_type = self.request.get("type")

		self.render("commentPage.html", food_value = food_id, food_type = food_type)

	def post(self):
		food_id = self.request.get("food")
		comment = self.request.get("comment")
		food_type = self.request.get("type")

		user_hash = self.request.cookies.get(PARAM_USER_ID, None)
		if user_hash is None:
			return
		userID = wutil.validateUser(user_hash)
		if userID is None:
			return # TODO return an identifiable error

		self.write("user: %s - foodID: %s - comment: %s" % (userID, food_id, comment))

		# strip html tags
		comment = dd.strip_tags(comment)
		# make comment and redirect
		dd.addComment(comment, int(food_id), userID)
		# redirect time
		refer = '/food/?type=%s' % food_type
		self.redirect(refer)


class VotePage(AppHandler):

	def post(self):
		food_id = self.request.get("food")
		vote = self.request.get("vote")
		
		user_hash = self.request.cookies.get(PARAM_USER_ID, None)
		if user_hash is None:
			return
		userID = wutil.validateUser(user_hash)
		if userID is None:
			return # TODO return an identifiable error

		expires = datetime.now() + timedelta(hours=1)
		dead_date = expires.strftime('%a, %d-%b-%Y %H:%M:%S')

		food_type = dd.castVote(vote, int(food_id), userID)
		self.response.headers.add_header('Set-Cookie', '%s=%s; Path=/; expires=%s;' % (str(food_id), str(vote), dead_date))

		# redirect time
		refer = self.request.headers["Referer"]
		self.redirect(refer)

