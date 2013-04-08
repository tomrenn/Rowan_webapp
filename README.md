Rowan_webapp

This application will provide web services for mobile clients [UPDATE: now includes a mobile website frontend]

-- currently a (very ugly) work in progress -- 

Below is documentation for the food rating system.

- DOCUMENTATION
================================
There are four different HTTP calls that are used to interact with the system. **All HTTP calls use GET, not POST.** This should be changed (to POST) for actions such as voting and commenting. API calls are as follows:

/food/createUser.json
==
Parameters:
 * ostype - [Optional] Something to describe the user-agent. i.e. Android Tablet, iPhone, iPod Touch

> A user is identified by an anonymous identifier. This identifier is required to vote and comment in the system. 

JSON Output:

	{"userID": "GENERATED HASH VALUE"}



/food/ratings
==
Parameters:
 * type - The type or location of ratings being requested. Available types: {"marketplace", "smokehouse"}

> Obtain the ratings and comments for a particular location. Ratings reset on a daily basis

JSON Output:

	{"entry":
		{
		"id"			: The ID representing the food entry,
	 	"created"		: Epoch time,
		"highestRating"	: previous all time percentage of upvotes to total votes,
	 	"lowestRating"	: previous all time percentage of downvotes to total votes,
	 	"totalVotes"	: The days current amount of votes,
		"upvotes"		: The days current number of upvotes
		}
	"comments":
		{
			0: {
				"comment": A simple string comment,
				"date"	 : Epoch time of posting
			}

			1: {
				"comment": "",
				"date"	 : ""
			}

			...

			n: {...}
		}
	}


/food/vote
==
Parameters:
 * userID	- the hash obtained by createUser.json
 * foodID	- the food ID of the entry being voted on
 * vote	- the vote, 1/0 corresponding to upvote/downvote

> Recording a vote to the selected entry.

JSON Output:
	
	N/A


/food/comment
==
Parameters:
 * userID	- the hash obtained by createUser.json
 * foodID	- the food ID of the entry receiving the comment
 * comment	- the comment being posted on the entry

> Recording a comment to the selected entry.

JSON Output:

	N/A
	