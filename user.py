from werkzeug.security import check_password_hash


class User():

	def __init__(self, user):
		self.username = user['_id']
		self.email = user['email']
		self.isDeveloper = user['isDeveloper']

	def is_authenticated(self):
		return True

	def is_active(self):
		return True

	def is_anonymous(self):
		return False
		
	def is_developer(self):
		return self.isDeveloper

	def get_id(self):
		return self.username

	@staticmethod
	def validate_login(user, password, isDeveloper):
		if isDeveloper != user['isDeveloper']:	# isDeveloper is the form data while logging in while user['isDeveloper'] is from db
			return False
		password_hash = user['password']
		return check_password_hash(password_hash, password)
	
	
	
	
	
	
	
	
	
	
	
	
	
	