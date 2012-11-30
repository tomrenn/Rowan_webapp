# functions to take objects and return json

import json

def generateReport(foodEntry, votes=None):

	commentsDict = {}
	count = 0;
	for vote in votes:
		if vote.comment != None:
			commentsDict[count] = {'comment' : vote.comment,
							   	   'date' : vote.commentDate.strftime('%s')}
			count += 1


	dictFormat = {'entry' : {'id' : foodEntry.key().id(),
							 'created' : foodEntry.created.strftime('%s'),
							 'highestRating' : foodEntry.highestRating,
							 'lowestRating'  : foodEntry.lowestRating,
							 'totalVotes' : foodEntry.totalVotes,
							 'upvotes' : foodEntry.upvotes 
							 },
				  'comments' : commentsDict
				 }
	return json.dumps(dictFormat)