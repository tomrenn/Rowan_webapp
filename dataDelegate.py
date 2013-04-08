# a list of functions to do information queries
import entities
from entities import db
from datetime import datetime, timedelta
from HTMLParser import HTMLParser

eastern_delta = timedelta(hours = 5)

def generateCommentsHTML(voteComments):
	html = ""
	for comment in voteComments:
		# make sure voteComment has a comment associated with it
		if comment.comment is None:
			continue

		html += '<div class="comment">'
		html += '	<div class="timestamp">'
		timePasted = datetime.now() - comment.commentDate
		minutes = int(timePasted.total_seconds() / 60)
		hours = int(timePasted.total_seconds() / 3600)
		timePasted = "Just now"
		if minutes == 1:
			timePasted = "%s minute ago" % minutes
		elif minutes > 1:
			timePasted = "%s minutes ago" % minutes

		if hours > 0:
			minutes = minutes - (hours*60)
			hourStr = "hours"
			minuteStr = "minutes"
			if hours == 1:
				hourStr = "hour"
			if minutes == 1:
				minuteStr = "minute"

			timePasted = "%s %s and %s %s ago" % (hours, hourStr, minutes, minuteStr)

		html += timePasted
		html += '	</div>'
		html += comment.comment
		html += '</div>'

	return html

# wonderful HTML tag stripper from http://stackoverflow.com/a/925630/121654
class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

# cast a vote, return the name of food_entry type
def castVote(vote, foodID, userID):
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

	return entry.name

def addComment(comment, foodID, userID):
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

# get last entry based on food type
def fetchRatings(food_type="marketplace"):

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

	return (entry, votes)