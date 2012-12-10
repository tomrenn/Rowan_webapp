import entities
from entities import db
import logging

import wutil # web utilties
import json
from handlers.base import AppHandler
from datetime import datetime, timedelta
#from datetime import datetime, timedelta
#from google.appengine.api import memcache

# used for turning UTC datetimes to EST(-5). Does not consider daylight savings
# TODO: look into datetime dst attribute
eastern_delta = timedelta(hours = 5)

PARAM_FOOD_TYPE = 'type' 
PARAM_FOOD_ID = 'foodID'
PARAM_OS_TYPE = 'ostype'
PARAM_USER_ID = 'userID'
PARAM_VOTE = 'vote'
PARAM_COMMENT = 'comment'

FOOD_MARKETPLACE = 'marketplace'
FOOD_SMOKEHOUSE  = 'smokehouse'


# TODO: make a web interface for showing ratings! ############################
class MainPage(AppHandler):
    def get(self):
      food_type = self.request.get(PARAM_FOOD_TYPE)
      self.write("type is as follows: %s" % food_type)


# Creates an anonymous user id, required for voting and commenting ###########  
# PARAMS
# OS_TYPE - provide the origin operating system of the user
class CreateUserJSON(AppHandler):
	def get(self):
		os_type = self.request.get(PARAM_OS_TYPE)

		# create a new anonymous user entity, give json response with hashed id
		new_user = entities.User(os_type = os_type)
		new_user.put()
		generated_hash = wutil.createSecret( new_user.key().id() )
		dictionary = {PARAM_USER_ID : generated_hash}
		self.response.headers['Content-Type'] = "application/json; charset=utf-8"
		self.write( json.dumps(dictionary) )

# Give JSON response of food ratings ########################################## 
# PARAMS
# FTYPE - which food type to return ratings
class ObtainRatingsJSON(AppHandler):
	def get(self):
		food_type = self.request.get(PARAM_FOOD_TYPE)
		if food_type not in (FOOD_MARKETPLACE, FOOD_SMOKEHOUSE):
			food_type = 'marketplace'

		# get last entry based on food type
		entry = db.GqlQuery("select * from FoodLocation where name = '%s' ORDER BY created DESC" % food_type);
		entry = entry.get() # get() retrieves 1 entry
		
		is_old_entry = False
		if entry is None: # No entry exists, create one
			entry = entities.FoodLocation(name = food_type, highestRating = 0.0, lowestRating = 0.0)
			entry.put()
		else: # check if entry is old 
			entry_date = entry.created - eastern_delta		
			now = datetime.now() - eastern_delta
			delta = now - entry_date

			if delta.days > 0 or now.day != entry_date.day:
				is_old_entry = True

		if is_old_entry: # update rating history, create new entry
			highestRating = entry.highestRating
			lowestRating = entry.lowestRating

			if entry.totalVotes != 0:
				rating = entry.upvotes / entry.totalVotes 
				if rating > highestRating:
					highestRating = float(rating)
				if rating < lowestRating:
					lowestRating = float(rating)
			
			entry = entities.FoodLocation(name = food_type, highestRating = highestRating, lowestRating = lowestRating)
			entry.put()

		# get votes/comments for the entry
		votes = db.GqlQuery("select * from FoodVote where foodLocationID=:1 ORDER BY commentDate DESC", entry.key().id())
		votes = votes.run()

		# generate and write result (JSON output string)
		import jsonutil
		result = jsonutil.generateReport(entry, votes)
		self.response.headers['Content-Type'] = "application/json; charset=utf-8"
		self.write(result)

# Page to vote on a food entry
# PARAMS
# USER - the user id hash
# VOTE - the vote to record, 0 or 1
# TYPE - The type to submit a vote for (can change this to submit type_id)
class VotePage(AppHandler):
	def get(self):
		user_hash = self.request.get(PARAM_USER_ID)
		userID = wutil.validateUser(user_hash)
		if userID is None:
			return # TODO return an identifiable error
		foodID = int(self.request.get(PARAM_FOOD_ID))
		vote 	  = self.request.get(PARAM_VOTE)

		if vote == '1':
			vote = 1
		else:
			vote = 0

		entry = entities.FoodLocation.get_by_id(foodID)

		food_vote = db.GqlQuery("select * from FoodVote where foodLocationID=%s and userID=%s" % (foodID, userID))
		food_vote = food_vote.get()

		if food_vote == None:
			food_vote = entities.FoodVote(userID = userID, foodLocationID = foodID, vote = vote, voteDate = datetime.now())
			entry.totalVotes += 1
			entry.upvotes += vote

		else:
			if food_vote.vote == -1: # food_vote exists because a comment was added before voting
				entry.totalVotes += 1
				entry.upvotes += vote

				food_vote.vote = vote
				food_vote.voteDate = datetime.now()

			else: # vote was changed
				if food_vote.vote == 0 and vote == 1: # went from downvote to upvote
					entry.upvotes += vote

					food_vote.vote = vote
					food_vote.voteDate = datetime.now()

				if food_vote.vote == 1 and vote == 0: # went from upvote to downvote
					entry.upvotes -= 1

					food_vote.vote = vote
					food_vote.voteDate = datetime.now()

		# commit changes
		entry.put()
		food_vote.put()

		# TODO: some kind of actual response
		self.response.headers['Content-Type'] = "application/json; charset=utf-8"


# page hanlder to submit comments ########################### 
# PARAMS
# USER - the user id hash
# COMMENT - the comment for the food entry
# TYPE - type to submit comment for, (change to type_id)
class VoteCommentPage(AppHandler):
	def get(self):
		user_hash = self.request.get(PARAM_USER_ID)
		userID = wutil.validateUser(user_hash)
		if userID is None:
			return # TODO return an identifiable error
		
		foodID = int(self.request.get(PARAM_FOOD_ID))
		comment   = self.request.get(PARAM_COMMENT)

		entry = entities.FoodLocation.get_by_id(foodID)

		# if user voted, there will be a food_vote entry already created
		food_vote = db.GqlQuery("select * from FoodVote where foodLocationID=%s and userID=%s" % (foodID, userID))
		food_vote = food_vote.get()

		if food_vote == None: # if no entry exists, create one
			food_vote = entities.FoodVote(userID = userID, foodLocationID = foodID, comment = comment, commentDate = datetime.now())
		else:
			food_vote.comment = comment
			food_vote.commentDate = datetime.now()
		food_vote.put()

		# TODO, respond with some kind of status code to indicate success
		self.response.headers['Content-Type'] = "application/json; charset=utf-8"

# irreleveant
class AnotherPage(AppHandler):
	def get(self):
		user_hash = self.request.get("user")

		user_id = user_hash.split('|')[0]
		if user_hash == wutil.createSecret(user_id):
			self.write( "success")
		else:
			self.write("failure")


