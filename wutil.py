import random
import string
import hmac
import hashlib

secret = "sup3rh4sh"

# creates a secret comprised of s|hash
def createSecret(s):
	if type(s) is not str:
		s = str(s)
	return "%s|%s" % (s, hmac.new(secret, s).hexdigest())

# generates 5 random letters
def generateSalt():
	return ''.join(random.choice(string.letters) for x in xrange(5))

# hash password with a salt - hash|salt
def hashPassword(name, pw, salt=None):
	if salt is None:
		salt = generateSalt()
	h = hashlib.sha256(name + pw + salt).hexdigest()
	return "%s|%s" % (h, salt)

# return validated user-id or -1 to represent invalid user
def validateUser(user_hash):
	userID = user_hash.split('|')[0]
	# check user id
	if createSecret(userID) != user_hash:
		return None
	else:
		return int(userID)
