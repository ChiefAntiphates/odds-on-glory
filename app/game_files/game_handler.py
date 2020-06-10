import time
import random as r
from flask_socketio import SocketIO, emit
from fractions import Fraction
from app.game_files.gladiator import *
from app.game_files.arena import *
from app.game_files.nameslist import *
from app.game_files.bank import *
from app.game_files.convertToJSON import pushInfoToJSON


#import tkinter as tk
#from tk_file import interfacePrintGrid

class GameHandler:
	
	def __init__(self, socketio, nspace, game_id): ##add size params
		self.socketio = socketio
		self.nspace = nspace
		self.game_id = game_id
		self.arena = Arena(8, 8, socketio, nspace) ##add size params
	
	
		for _ in range(4):
			self.arena.addGladiator(Gladiator(r.choice(nameslist), r.randrange(99), 
					r.randrange(30,99), r.randrange(99)))
		self.arena.prepareOdds()
		
	def getJSON(self):
		return pushInfoToJSON(self.arena)
		
	#def addGladiator:
		##Add remaining if 30 seconds left and remaining places
		##Once max gladiators added calculate the odds
	
	#def tempGoForThis(self):
		#for _ in range(3):
			#self.preGameDisplay()
			#self.socketio.sleep(3)
	
	def preGameDisplay(self):
		#Perhaps do a while loop here lasting over 30 1 second increments before starting games
		json_obj = pushInfoToJSON(self.arena)
		self.socketio.emit('arenaupdate', {'json_obj': json_obj}, namespace=self.nspace)
	
	def startGames(self):
		while len(self.arena.gladiators) > 1:
			self.arena.nextTurn()
		
		print("game over")
		if len(self.arena.gladiators) > 0:
			self.arena.af.updateActivityFeed("WINNER", "%s wins!" % self.arena.gladiators[0].name)
			#betting stuff
		else:
			self.arena.af.updateActivityFeed("GAME OVER", "So everyone died. There are no winners.")
		
		
		
		
		
		
		
		
		
		
		