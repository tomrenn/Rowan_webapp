from google.appengine.ext import db 

# represent an anonymous user, default incremented ID will be used as the unique key 
class User(db.Model):
  os_type = db.StringProperty()
  created = db.DateTimeProperty(auto_now_add = True)

class FoodLocation(db.Model):
	name = db.StringProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)
	highestRating = db.FloatProperty()
	lowestRating  = db.FloatProperty()
	totalVotes = db.IntegerProperty(default = 0)
	upvotes = db.IntegerProperty(default = 0)

class FoodVote(db.Model):
	foodLocationID = db.IntegerProperty(required = True)
	userID = db.IntegerProperty(required = True)
	vote = db.IntegerProperty(default = -1)
	voteDate = db.DateTimeProperty()
	comment = db.StringProperty()
	commentDate = db.DateTimeProperty()

