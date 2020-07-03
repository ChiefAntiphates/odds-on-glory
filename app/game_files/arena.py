import time
import random as r
from threading import Thread
#import tkinter as tk
from app.game_files.tile import *
from app.game_files.gladiator import *
from app.game_files.bank import *
from functools import partial
from app.game_files.nameslist import *
from app.game_files.convertToJSON import pushInfoToJSON
import sys


TIMER = 0.7 ##How long should each turn take??
SCORCH = 1 #How many turns before scorchTheEarth
class Arena:
	
	'''CONSTRUCTOR'''
	def __init__(self, width, height, socketio, nspace):
		self.height = height
		self.width = width
		self.duration = 1 
		self.active = False
		self.gladding = True
		self.gladiators = []
		self.runners = []
		self.dead_gladiators = []
		self.odds_on = None
		self.active_battles = []
		self.scorch_level = 0
		self.edge_tiles = []
		self.af = ActivityFeed()
		self.af.updateActivityFeed("ENTRY PHASE", "Enter your gladiator before time runs out!")
		self.socketio = socketio
		self.nspace = nspace
		self.packed=False
		
		self.grid = [[Tile(a,b) for a in range(self.width)] for b in range(self.height)]	
		for row in self.grid:
			for tile in row:
				if (tile.x_pos == 0) or (tile.y_pos == 0) or (tile.x_pos == self.width-1) or (tile.y_pos == self.height-1): 
					tile.edge = True
					self.edge_tiles.append(tile)
	
	
	
	def getGladiator(self, gladiator):
		#ensure gladiators not placed next to each other
		if self.packed:
			tile = r.choice([tile for tile in self.edge_tiles if not(tile.occupied)])
		else:
			tile = r.choice([tile for tile in self.edge_tiles if not(tile.occupied) 
				and len([tile for tile in self.getTileSurroundings(tile) if tile.occupied]) < 1])
		tile.setGladiatorToTile(gladiator)
		self.gladiators.append(gladiator)
		gladiator.setArena(self)
		gladiator.setPosition(tile.x_pos, tile.y_pos)
		self.prepareOdds()
		print(gladiator.id)
		
	def addRunner(self, runner):
		try:
			tile = r.choice([tile for tile in self.edge_tiles if not(tile.occupied)])
			tile.setGladiatorToTile(runner)
		except IndexError as e:
			tile = r.choice([tile for tile in self.edge_tiles])
			tile.setGladiatorToTile(runner)
			
		self.runners.append(runner)
		runner.setArena(self)
		runner.setPosition(tile.x_pos, tile.y_pos)
	
	def prepareOdds(self):
		self.odds_on = calculateOdds(self.gladiators)
		
	
	def nextTurn(self):
		if (self.duration % SCORCH == 0): #Scorch earth every 10 turns
			self.scorchTheEarth()
			
		for runner in sorted(self.runners, key=lambda x: x.speed, reverse=True):
			runner.executeTurn()
		##Move all runners simultaneuosly (in perception)
		
			json_obj = pushInfoToJSON(self)
			self.socketio.emit('arenaupdate', {'json_obj': json_obj}, namespace=self.nspace)
			self.socketio.sleep(TIMER/2)
		####################################################
			
		for gladiator in sorted(self.gladiators, key=lambda x: x.speed, reverse=True):
			##Maybe when high volume do a couple of turns simultaneuosly
			gladiator.executeTurn()
			
			json_obj = pushInfoToJSON(self)
			self.socketio.emit('arenaupdate', {'json_obj': json_obj}, namespace=self.nspace)
			self.socketio.sleep(TIMER)
			
		self.odds_on = calculateOdds(self.gladiators)
		self.duration += 1
		
		
		
	def getTileSurroundings(self, input_tile):
		x = input_tile.x_pos
		y = input_tile.y_pos
		tiles = []
		for i in range(len(self.grid)):
			for j in range(len(self.grid[0])):
				if (abs(y-i)<=1 and abs(x-j)<=1):
					
					if self.grid[i][j].hostile == False:
						tiles.append(self.grid[i][j])
		
		
		if (input_tile in tiles):
			tiles.remove(input_tile)
			
		return(tiles)
		
	
	
	
	##Reduce size of battlefield
	def scorchTheEarth(self):
		for i in range(len(self.grid)): #y
			for j in range(len(self.grid[0])): #x
				if (i == self.scorch_level) or (i == len(self.grid)-1-self.scorch_level):
					self.grid[i][j].setHostile()
				elif (j == self.scorch_level) or (j == len(self.grid[0])-1-self.scorch_level):
					self.grid[i][j].setHostile()
		self.scorch_level += 1
	
	'''##MOVED INTO GAME HANDLER
	##Sends a trap of fixed damage 50 to a gladiator
	def sendGladiatorTrap(self, gladiator):
		self.addRunner(Runner(r.choice(nameslist), r.randrange(15), 0, r.randrange(30,99), gladiator, [Gladiator.I_TRAPS, Trap(50, None)]))
	'''				
	
		
	
	
	
	
	
	
	
	
			