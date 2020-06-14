import time
import random as r
from flask_socketio import SocketIO, emit
from fractions import Fraction
from app.game_files.gladiator import *
from app.game_files.arena import *
from app.game_files.nameslist import *
from app.game_files.bank import *
from app.game_files.convertToJSON import pushInfoToJSON

from app import app, db, socketio
from app.models import User, Post, Tournament


BETTING_PHASE_TIME = 2


#import tkinter as tk
#from tk_file import interfacePrintGrid

class GameHandler:
	
	def __init__(self, socketio, nspace, game_id): ##add size params
		self.socketio = socketio
		self.nspace = nspace
		self.game_id = game_id
		self.arena = Arena(8, 8, socketio, nspace) ##add size params
		self.bets = []
	
		##Workflow should be as follows
		'''
			1 - Arena is created with preset size -small, med, large with max glads for each
			2 - Gladiators added over the space of 1 or 2 mins
			3 - Arena and glads displayed to user for 30 seconds
			4 - game begins
		'''		
		
		
		
	def getJSON(self):
		return pushInfoToJSON(self.arena)
		
		
	def addGladiator(self):
	#def addGladiator(gladiator stats):
		self.arena.getGladiator(Gladiator(r.choice(nameslist), r.randrange(99), 
						r.randrange(30,99), r.randrange(99)))
		##Add remaining if 30 seconds left and remaining places
		##Once max gladiators added calculate the odds
	
	
	def sendBet(self, glad_id, bet_value, punter_id):
		gladiator = next((x for x in self.arena.gladiators if int(x.id) == int(glad_id)), None)
		self.bets.append(Bet(self.arena, gladiator, bet_value, punter_id)) 
		
	
	def sendGift(self, glad_id, gift): ##And runner as param #Currently all gifts are traps
		gladiator = next((x for x in self.arena.gladiators if int(x.id) == int(glad_id)), None)
		#runner  = Runner(r.choice(nameslist), r.randrange(15), 0, r.randrange(30,99), gladiator, gift))
		runner = Runner(r.choice(nameslist), r.randrange(15), 0, r.randrange(30,99), gladiator, [Gladiator.I_TRAPS, Trap(50, None)])
		self.arena.addRunner(runner)
	
	
	def preGame(self):
		#Spend x amount of time getting new gladiators
		for _ in range(10):
			self.socketio.sleep(1)
			
			
			json_obj = pushInfoToJSON(self.arena)
			self.socketio.emit('gladiatoradding', {'json_obj': json_obj}, namespace=self.nspace)
			#if len(self.arena.gladiators) == glad_max: break
		
		self.arena.active = True
		self.socketio.emit('arenainitial', {'json_obj': json_obj}, namespace=self.nspace)	
		self.socketio.sleep(BETTING_PHASE_TIME)
		self.startGames()
	
	def startGames(self):
		while len(self.arena.gladiators) > 1:
			self.arena.nextTurn()
		
		print("game over")
		if len(self.arena.gladiators) > 0:
			self.arena.af.updateActivityFeed("WINNER", "%s wins!" % self.arena.gladiators[0].name)
			self.payOut(self.arena.gladiators[0])
			#betting stuff
		else:
			self.arena.af.updateActivityFeed("GAME OVER", "So everyone died. There are no winners.")
		json_obj = pushInfoToJSON(self.arena)
		self.socketio.emit('arenaupdate', {'json_obj': json_obj}, namespace=self.nspace)
		
	
	
	def payOut(self, winner):
		for bet in self.bets:
			if (bet.gladiator == winner):
				punter = User.query.filter_by(id=bet.punter_id).first()
				punter.addMoney(bet.betReturn)
				db.session.commit()
		
		
		
		
		
		
		