import time
import random as r
from threading import Thread
import tkinter as tk
from app.game_files.tile import *
from app.game_files.gladiator import *
from app.game_files.bank import *
from functools import partial
from app.game_files.tk_file import interfacePrintGrid
from app.game_files.nameslist import *
import sys

TIMER = 500

class Arena:
	
	'''CONSTRUCTOR'''
	def __init__(self, width, height):
		self.height = height
		self.width = width
		self.duration = 12 # Units of 30 minutes - 48 units in one day
		self.active = False
		self.gladiators = []
		self.runners = []
		self.dead_gladiators = []
		self.odds_on = None
		self.bets_made = []
		self.active_battles = []
		self.scorch_level = 0
		self.edge_tiles = []
		
		self.grid = [[Tile(a,b) for a in range(self.width)] for b in range(self.height)]	
		for row in self.grid:
			for tile in row:
				if (tile.x_pos == 0) or (tile.y_pos == 0) or (tile.x_pos == self.width-1) or (tile.y_pos == self.height-1): 
					tile.edge = True
					self.edge_tiles.append(tile)
					
		
		
		#################
		###Tk Activity###
		self.window = tk.Tk()
		
		self.frame = tk.Frame(self.window)
		self.frame.grid(row=0, column=1, rowspan=2, sticky="N")
		tk.Grid.columnconfigure(self.window, 1, weight=1)
		
		self.activity_frame = tk.Frame(self.window)
		self.activity_frame.grid(row=0, column=2, sticky="N", padx=75)
		
		self.battles_frame = tk.Frame(self.window)
		self.battles_frame.grid(row=1, column=2, sticky="N", padx=75)
		
		self.gladiator_frame = tk.Frame(self.window)
		self.gladiator_frame.grid(row=0, column=0, padx=40, sticky="N")
		
		self.dead_gladiator_frame = tk.Frame(self.window)
		self.dead_gladiator_frame.grid(row=1, column=0, padx=40, sticky="N")
		
		
		self.datetext = tk.Label(self.activity_frame, text="")
		self.datetext.pack()
		self.timetext = tk.Label(self.activity_frame, text="")
		self.timetext.pack()
		tk.Label(self.battles_frame, text="Active Battles", font='Calibri 10 bold').pack()
		tk.Label(self.activity_frame, text="Activity Feed", font='Calibri 10 bold').pack()
		tk.Label(self.activity_frame, text="-------------", font='Calibri 10 bold').pack()
		
		#End Tk Activity#
		#################
		
		self.af = ActivityFeed(self.activity_frame) # semi tk related because Activity requires frame
		
		
	#########################	
	################TK STUFF##
	def reset(self):##tk stuff
		self.window.destroy()
		try:
			del sys.modules["main"]
		except KeyError:
			pass
		import main
	def advance(self):
		#while pause:
			#pass
		self.window.quit()
	#########################
	#########################
	
	
	
	def addGladiator(self, gladiator):
		#ensure gladiators not placed next to each other
		tile = r.choice([tile for tile in self.edge_tiles if not(tile.occupied) 
			and len([tile for tile in self.getTileSurroundings(tile) if tile.occupied]) < 1])
		tile.setGladiatorToTile(gladiator)
		self.gladiators.append(gladiator)
		gladiator.setArena(self)
		gladiator.setPosition(tile.x_pos, tile.y_pos)
		
	def addRunner(self, runner):
		tile = r.choice([tile for tile in self.edge_tiles if not(tile.occupied)])
		tile.setGladiatorToTile(runner)
		self.runners.append(runner)
		runner.setArena(self)
		runner.setPosition(tile.x_pos, tile.y_pos)
	
	def prepareOdds(self):
		self.odds_on = calculateOdds(self.gladiators)
		
	
	def nextTurn(self):
		if (self.duration % 48 == 36):
			self.scorchTheEarth()
			
		for runner in sorted(self.runners, key=lambda x: x.speed, reverse=True):
			runner.executeTurn()
		##Move all runners simultaneuosly (in perception)
		#time.sleep(0.4)
		
		##Add to a queue with game ID?????? Use get function to pop from queue 
		###########################tk stuff##
		self.window.after(TIMER, self.advance)#timer
		self.window.mainloop()
		interfacePrintGrid(self)
		########################
			
		for gladiator in sorted(self.gladiators, key=lambda x: x.speed, reverse=True):
			##Maybe when high volume do a couple of turns simultaneuosly
			gladiator.executeTurn()
			#time.sleep(0.4)
			
			###tk stuff## here if update after each glad action##
			self.window.after(TIMER, self.advance)#timer
			self.window.mainloop()
			interfacePrintGrid(self)
			print(self.odds_on)
			############################################
			
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
	
	##Sends a trap of fixed damage 50 to a gladiator
	def sendGladiatorTrap(self, gladiator):
		self.addRunner(Runner(r.choice(nameslist), r.randrange(15), 0, r.randrange(30,99), gladiator, [Gladiator.I_TRAPS, Trap(50, None)]))
					
	
	##Create bet -> REQUIRED TK STUFF ##########
	def prepareBet(self, gladiator):
		'''def placeBet(value, gladiator):
			bet_win.destroy()
			self.bets_made.append(Bet(self, gladiator, value))
			
		bet_win = tk.Toplevel(self.window)
		bet_win.minsize(220,175)
		tk.Label(bet_win, text="Bet how much on %s?" % gladiator.name).pack()
		value_input = tk.Entry(bet_win)
		value_input.pack()
		tk.Button(bet_win, text="Place Bet",
				command=lambda : placeBet(value_input.get(), gladiator)).pack()'''
		##Default currently at betting 50 coins
		self.bets_made.append(Bet(self, gladiator, 50))
	########REQUIRED TK STUFF ##########			
				
	def betWon(self, bet):
		print("You won %s" % bet.betReturn)
		
	
	
	
	
	
	
	
	
			