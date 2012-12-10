# functions to take objects and return json

import json
import time
def generateReport(foodEntry, votes=None):

	commentsDict = {}
	count = 0;
	for vote in votes:
		if vote.comment != None:
			commentsDict[count] = {'comment' : vote.comment,
							   	   'date' : time.mktime(vote.commentDate.timetuple())}
			count += 1


	dictFormat = {'entry' : {'id' : foodEntry.key().id(),
							 'created' : time.mktime(foodEntry.created.timetuple()),
							 'highestRating' : foodEntry.highestRating,
							 'lowestRating'  : foodEntry.lowestRating,
							 'totalVotes' : foodEntry.totalVotes,
							 'upvotes' : foodEntry.upvotes 
							 },
				  'comments' : commentsDict
				 }
	return json.dumps(dictFormat)