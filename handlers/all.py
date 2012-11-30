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
eastern_delta = timedelta(hours = 5)

# Shows all the blog posts
class MainPage(AppHandler):

    def get(self):
      #self.write("hello world") 
      food_type = self.request.get("type")
      self.write("type is as follows: %s" % food_type)


# Creates a new user and responds with a JSON representation
class CreateUserJSON(AppHandler):
	def get(self):
		os_type = self.request.get("ostype")

		# create a new anonymous user
		new_user = entities.User(os_type = os_type)
		new_user.put()

		# create secret with User ID
		generated_hash = wutil.createSecret( new_user.key().id() )

		dictionary = {'userID' : generated_hash}

		self.response.headers['Content-Type'] = "application/json; charset=utf-8"

		self.write( json.dumps(dictionary) )

class ObtainRatingsJSON(AppHandler):
	def get(self):
		food_type = self.request.get('type')
		# temp
		if food_type == '':
			food_type = 'marketplace'

		# get last entry based on food type
		entry = db.GqlQuery("select * from FoodLocation where name = '%s' ORDER BY created DESC" % food_type);
		# get() retrieves only 1 entry
		entry = entry.get()

		is_old_entry = False

		if entry is None:
			#self.write("no entry is found")
			# creating new entry
			entry = entities.FoodLocation(name = food_type, highestRating = 0.0, lowestRating = 0.0)
			entry.put()
		else:
			# localize entry date to eastern timezone
			entry_date = entry.created - eastern_delta		
			now = datetime.now() - eastern_delta
			delta = now - entry_date

			# if the delta is more than a day old... or day is different from last entry
			if delta.days > 0 or now.day != entry_date.day:
				is_old_entry = True

		# previous entry is a day old
		if is_old_entry:
			# check if yesterdays rating set a record
			highestRating = entry.highestRating
			lowestRating = entry.lowestRating

			if entry.totalVotes != 0:
				rating = entry.upvotes / entry.totalVotes 
				if rating > highestRating:
					highestRating = float(rating)
				if rating < lowestRating:
					lowestRating = float(rating)
			
			#self.write("<br> <span style='color:red;'> created new entry </span>")

			entry = entities.FoodLocation(name = food_type, highestRating = highestRating, lowestRating = lowestRating)
			entry.put()

		# entry is now valid for the current day

		# now we have a correct entry
		votes = db.GqlQuery("select * from FoodVote where foodLocationID=:1 ORDER BY commentDate DESC", entry.key().id())
		votes = votes.run()

		# function to generate JSON...
		import jsonutil
		result = jsonutil.generateReport(entry, votes)
		self.response.headers['Content-Type'] = "application/json; charset=utf-8"
		self.write(result)

# There is no check if a user has previously voted for the FoodLocation entity
class VotePage(AppHandler):
	def get(self):
		user_hash = self.request.get("user")
		userID = user_hash.split('|')[0]
		# check user ID
		if wutil.createSecret(userID) != user_hash:
			self.write('Invalid user %s for %s' % (wutil.createSecret(userID), user_hash))
			return
		else:
			userID = int(userID)
		foodID = int(self.request.get("type"))
		vote 	  = self.request.get("vote")

		# format given vote - 0 if none given, convert '1' or '0' to int
		if vote == '':
			vote = 0
		else:
			vote = int(vote)

		#self.write("vote = %s" % vote)
		entry = entities.FoodLocation.get_by_id(foodID)

		# now to create or modify a FoodVote
		food_vote = db.GqlQuery("select * from FoodVote where foodLocationID=%s and userID=%s" % (foodID, userID))
		food_vote = food_vote.get()

		self.response.headers['Content-Type'] = "application/json; charset=utf-8"
		#self.write('<br> foodID: %s - userID: %s ' % (foodID, userID))


		if food_vote == None:
			food_vote = entities.FoodVote(userID = userID, foodLocationID = foodID, vote = vote, voteDate = datetime.now())
			entry.totalVotes += 1
			entry.upvotes += vote
		else:
			if food_vote.vote == -1:
				# food_vote exists because they added a comment before voting
				food_vote.vote = vote
				food_vote.voteDate = datetime.now()
				# update food entry
				entry.totalVotes += 1
				entry.upvotes += vote
			else:
				# vote was changed
				# went from downvote to upvote
				if food_vote.vote == 0 and vote == 1: 
					entry.upvotes += vote

					food_vote.vote = vote
					food_vote.voteDate = datetime.now()
				# went from upvote to downvote
				if food_vote.vote == 1 and vote == 0: 
					entry.upvotes -= 1

					food_vote.vote = vote
					food_vote.voteDate = datetime.now()

		# submit changes
		entry.put()
		food_vote.put()

class VoteCommentPage(AppHandler):
	def get(self):
		user_hash = self.request.get("user")
		userID = user_hash.split('|')[0]
		#check user id
		if wutil.createSecret(userID) != user_hash:
			self.write('Invalid user')
			return
		else:
			userID = int(userID)
		foodID = int(self.request.get("type"))
		comment   = self.request.get("comment")
		#self.write(comment)

		entry = entities.FoodLocation.get_by_id(foodID)

		food_vote = db.GqlQuery("select * from FoodVote where foodLocationID=%s and userID=%s" % (foodID, userID))
		food_vote = food_vote.get()

		if food_vote == None:
			food_vote = entities.FoodVote(userID = userID, foodLocationID = foodID, comment = comment, commentDate = datetime.now())
		else:
			food_vote.comment = comment
			food_vote.commentDate = datetime.now()
		food_vote.put()

		# simply for iOS json request to recieve json
		self.response.headers['Content-Type'] = "application/json; charset=utf-8"


class AnotherPage(AppHandler):
	def get(self):
		user_hash = self.request.get("user")

		user_id = user_hash.split('|')[0]
		if user_hash == wutil.createSecret(user_id):
			self.write( "success")
		else:
			self.write("failure")


