from datetime import datetime
from time import time
import jwt
import json
from app import db, login, app

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from hashlib import md5

@login.user_loader
def load_user(id):
	return User.query.get(int(id))
	

class Tournament(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	code = db.Column(db.String(120), index=True, unique=True)
	size = db.Column(db.String(16))
	density = db.Column(db.String(16))
	owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	name = db.Column(db.String(32))
	#Introduce "state" idea like in progress or betting/gladding phase

	def __repr__(self):
		return '<Game {}>'.format(self.id)
		
	def set_code(self):
		self.code = ('/gsockname'+str(self.id))




class Gladiator(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), index=True)
	strength = db.Column(db.Integer, index=True)
	speed = db.Column(db.Integer, index=True)
	aggro = db.Column(db.Integer, index=True)
	height = db.Column(db.String(32))
	bio = db.Column(db.String(250))
	quote = db.Column(db.String(140))
	
	available = db.Column(db.Boolean)#False if in Arena
	owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	
	elims = db.Column(db.Integer, index=True)
	
	battle_ready = db.Column(db.Integer, index=True, default=100)
	last_update = db.Column(db.DateTime, default=datetime.utcnow)#last fight
	
	def __repr__(self):
		return '<Gladiator {}>'.format(self.name)
		
	
	def getJSON(self):
		return {"id": self.id, "name": self.name, "strength": self.strength,
					"speed": self.speed, "aggro": self.aggro, 
					"battle_ready": self.battle_ready}
	
	def getPrice(self):
		return round((self.speed*0.6)+(self.strength*3)+(self.aggro*0.2))
		
		



class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True, unique=True)
	email = db.Column(db.String(120), index=True, unique=True)
	password_hash = db.Column(db.String(128))
	money = db.Column(db.Integer)
	money_rank = db.Column(db.Integer)
	
	last_bonus = db.Column(db.DateTime, default=datetime.utcnow)
	
	gladiators = db.relationship('Gladiator', backref='owner', lazy='dynamic')
	hosted_games = db.relationship('Tournament', backref='host', lazy='dynamic')
	
	
	def addMoney(self, value):
		self.money = self.money + value
		
	def spendMoney(self, value):
		self.money = self.money - value
		
	def getAvailGlads(self):
		json_obj = []
		for glad in self.gladiators:
			if glad.available:
				json_obj.append(glad.getJSON())
		return json.dumps(json_obj[::-1])
		
	
	def __repr__(self):
		return '<User {}>'.format(self.username)
		
	def set_password(self, password):
		self.password_hash = generate_password_hash(password)
	
	def check_password(self, password):
		return check_password_hash(self.password_hash, password)
	
	def avatar(self, size):
		digest = md5(self.email.lower().encode('utf-8')).hexdigest()
		return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)
	
	'''
	def follow(self, user):
		if not self.is_following(user):
			self.followed.append(user)
	
	def unfollow(self, user):
		if self.is_following(user):
			self.followed.remove(user)
	
	def is_following(self, user):
		return self.followed.filter(
			followers.c.followed_id == user.id).count() > 0
			
	def followed_posts(self):
		followed =  Post.query.join(
			followers, (followers.c.followed_id == Post.user_id)).filter(
				followers.c.follower_id == self.id)
		own = Post.query.filter_by(user_id=self.id)
		return followed.union(own).order_by(Post.timestamp.desc())
	'''
	
	def get_reset_password_token(self, expires_in=600):
		return jwt.encode(
			{'reset_password': self.id, 'exp': time() + expires_in},
			app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')
	
	@staticmethod
	def verify_reset_password_token(token):
		try:
			id = jwt.decode(token, app.config['SECRET_KEY'],
					algorithms=['HS256'])['reset_password']
		except:
			return
		return User.query.get(id)
		

'''
class Post(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	body = db.Column(db.String(140))
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	
	def __repr__(self):
		return '<Post {}>'.format(self.body)
'''




