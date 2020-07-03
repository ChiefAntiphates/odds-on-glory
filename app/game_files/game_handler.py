import time
import json
import random as r
from flask_socketio import SocketIO, emit
from fractions import Fraction
from app.game_files.gladiator import *
from app.game_files.arena import *
from app.game_files.nameslist import nameslist
from app.game_files.bank import *
from app.game_files.convertToJSON import pushInfoToJSON

from app import app, db, socketio
from app.models import User, Tournament
from app.models import Gladiator as dbGladiator

GLAD_ADD_TIME = 20##change time
BETTING_PHASE_TIME = 20


#import tkinter as tk
#from tk_file import interfacePrintGrid

class GameHandler:
	
	def __init__(self, socketio, nspace, game_id, size, density): ##add size params
		
		##SORT OUT THE SIZES HERE PLEASE
		if (size=='small'):
			self.arena = Arena(8, 5, socketio, nspace)
			if (density=='sparse'):
				self.capacity=4
			elif (density=='normal'):
				self.capacity=7
			else:
				self.capacity=12
				self.arena.packed = True
		elif (size=='medium'):
			self.arena = Arena(10, 7, socketio, nspace)
			if (density=='sparse'):
				self.capacity=7
			elif (density=='normal'):
				self.capacity=10
			else:
				self.capacity=14
				self.arena.packed = True
		else:
			self.arena = Arena(13, 8, socketio, nspace)
			if (density=='sparse'):
				self.capacity=10
			elif (density=='normal'):
				self.capacity=14
			else:
				self.capacity=20
				self.arena.packed = True
				
		self.socketio = socketio
		self.nspace = nspace
		self.game_id = game_id
		
		self.bets = []
		self.user_activity = []
		self.barred_users = set()
	
		##Workflow should be as follows
		'''
			1 - Arena is created with preset size -small, med, large with max glads for each
			2 - Gladiators added over the space of 1 or 2 mins
			3 - Arena and glads displayed to user for 30 seconds
			4 - game begins
		'''		
		
		
		
	def getJSON(self):
		return pushInfoToJSON(self.arena)
		
		
	def addGladiator(self, name, strength, aggro, speed, ext_id=None, champion="The State", owner_id=None):
		if (len(self.arena.gladiators) < self.capacity):
			self.arena.getGladiator(Gladiator(name, strength, aggro, speed, ext_id, owner_id, champion))
		
		self.barred_users.add(owner_id)
		self.user_activity.append("%s entered %s to the arena." % (champion, name))
		
		self.socketio.emit('useractivityupdate', {'all_bets': self.convertBetsToJSON(), 'user_activity': self.user_activity}, namespace=self.nspace)
		
		#else emit an error message!!!
	
	
	def sendBet(self, glad_id, bet_value, punter_id):
		gladiator = next((x for x in self.arena.gladiators if int(x.id) == int(glad_id)), None)
		self.bets.append(Bet(self.arena, gladiator, bet_value, punter_id)) 
		
		punter = User.query.filter_by(id=punter_id).first()
		punter.spendMoney(int(bet_value))
		db.session.commit()
		
		self.user_activity.append("%s bet %s on %s." % (punter.username, bet_value, gladiator.name))
		
		#move to one socket update for general activity
		self.socketio.emit('useractivityupdate', {'all_bets': self.convertBetsToJSON(), 'user_activity': self.user_activity}, namespace=self.nspace)
		
	
	def sendGift(self, glad_id, gift, cost, sender_id): ##And runner as param #Currently all gifts are traps
		gladiator = next((x for x in self.arena.gladiators if int(x.id) == int(glad_id)), None)
		#runner  = Runner(r.choice(nameslist), r.randrange(15), 0, r.randrange(30,99), gladiator, gift))
		sender = User.query.filter_by(id=sender_id).first()
		sender.spendMoney(int(cost))
		db.session.commit()
		runner = Runner(r.choice(nameslist), r.randrange(15), 0, r.randrange(30,99), gladiator, [Gladiator.I_TRAPS, Trap(50, None)])
		
		self.arena.addRunner(runner)
		
		self.user_activity.append("%s sent %s a trap." % (sender.username, gladiator.name))
		
		#move to one socket update for general activity
		self.socketio.emit('useractivityupdate', {'all_bets': self.convertBetsToJSON(), 'user_activity': self.user_activity}, namespace=self.nspace)
	
	
	
	##Allowing for adding gladiators
	def preGame(self):
		#Spend x amount of time getting new gladiators
		for i in range(GLAD_ADD_TIME):
			
			if (i == (GLAD_ADD_TIME-1)):
			#Add gladiators into empty spaces	
				while (len(self.arena.gladiators) < self.capacity):
					self.addGladiator(r.choice(nameslist), r.randrange(99),
										r.randrange(30,99), r.randrange(99))
			
			
			json_obj = pushInfoToJSON(self.arena)
			self.socketio.emit('gladiatoradding', {'json_obj': json_obj, 'timer': GLAD_ADD_TIME-i-1}, namespace=self.nspace)
			if (len(self.arena.gladiators) >= self.capacity):
				break
			self.socketio.sleep(1)	
			
			
		
		self.arena.gladding = False
		self.arena.af.updateActivityFeed("BETTING PHASE", "Place your first bets on gladiators before the game starts for the best odds!")
		json_obj = pushInfoToJSON(self.arena)
		self.socketio.emit('arenainitial', {'json_obj': json_obj}, namespace=self.nspace)	
		for i in range(BETTING_PHASE_TIME):
			self.socketio.emit('arenabetting', {'timer': BETTING_PHASE_TIME-i-1}, namespace=self.nspace)
			self.socketio.sleep(1)
			
		self.startGames()
	
	
	
	
	def startGames(self):
		self.arena.active = True
		while len(self.arena.gladiators) > 1:
			self.arena.nextTurn()
		
		
		print("game over")
		if len(self.arena.gladiators) < 1:
			self.arena.af.updateActivityFeed("GAME OVER", "So everyone died. There are no winners.")
		
			#betting stuff
		else:
			self.arena.af.updateActivityFeed("WINNER", "%s wins!" % self.arena.gladiators[0].name)
			self.payOut(self.arena.gladiators[0])
			json_obj = pushInfoToJSON(self.arena)
			
			self.socketio.emit('arenaupdate', {'json_obj': json_obj}, namespace=self.nspace)
			#Final emit to clean up
			win_id = self.arena.gladiators[0].ext_id
			if (self.arena.gladiators[0].ext_id == None):
				win_id = "None"
			
			self.socketio.emit('arenafinish', {'winner': win_id}, namespace=self.nspace)
			if (win_id != "None"):
				gladiator = dbGladiator.query.filter_by(id=win_id).first()
				gladiator.available = True
				gladiator.last_update = datetime.utcnow()
				gladiator.battle_ready = 0
				db.session.commit()
				win_owner = gladiator.owner
				winnings = 500
				win_owner.addMoney(winnings)
				db.session.commit()
				self.socketio.emit('gladwon', {'glad': gladiator.name, 'winnings': winnings}, 
								namespace="/"+str(gladiator.owner.id))
				print("player glad wins")
			else:
				print("non player glad wins")
				
		game = Tournament.query.filter_by(id=self.game_id).first()
		db.session.delete(game)
		db.session.commit()
		

		
	
	
	def payOut(self, winner):
		for bet in self.bets:
			if (bet.gladiator == winner):
				punter = User.query.filter_by(id=bet.punter_id).first()
				punter.addMoney(bet.betReturn)
				db.session.commit()
				self.socketio.emit('betwin', {'glad': bet.gladiator.name, 'winnings': bet.betReturn}, 
							namespace="/"+str(bet.punter_id))
			
	def convertBetsToJSON(self):
		bets_json = {"bets": []}
		for bet in self.bets:
			bet_info = {}
			bet_info["punter_id"] = bet.punter_id
			bet_info["gladiator"] = bet.gladiator.name
			bet_info["glad_id"] = bet.gladiator.id
			bet_info["alive"] = bet.gladiator.alive
			bet_info["odds"] = bet.odds_info[2]
			bet_info["value"] = bet.bet
			bet_info["return_val"] = bet.betReturn
			bets_json["bets"].append(bet_info)
		return bets_json
		
		
		
		
		