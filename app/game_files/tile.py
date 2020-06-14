import time
import random
from app.game_files.gladiator import *
from app.game_files.trap import *
from app.game_files.activity_feed import *

class Tile:
	
	'''CONSTRUCTOR'''
	def __init__(self, x_co, y_co):
		self.occupied = False
		self.occupants = []
		self.corpses = []
		self.x_pos = x_co
		self.y_pos = y_co
		self.edge = False
		self.hostile = False
		
		self.trap_present = False
		self.trap = None
		
		
	def setGladiatorToTile(self, gladiator):
		self.occupied = True
		self.occupants.append(gladiator)
		if self.trap_present:#Have a maybe modifier
			if gladiator != self.trap.owner: #cant be damaged by own trap
				self.trapTripped(gladiator)
		
	
	def removeGladiator(self, gladiator):
		self.occupants.remove(gladiator)
		if len(self.occupants) == 0:
			self.occupied = False

	def toString(self):
		if self.occupied == False:
			return ""
		elif self.occupied == True:
			return ("%s" % "\n".join([occupant.initial for occupant in self.occupants]))

	def setHostile(self):
		self.hostile = True
		
	def setTrapToTile(self, trap):
		self.trap_present = True
		self.trap = trap
		
		
	def trapTripped(self, gladiator):
		self.trap.activateTrap(gladiator)
		self.trap_present = False
		del self.trap
		self.trap = None
	
	def getItemsFromBodies(self):
		loot = []
		for body in self.corpses:
			for item_type in body.inventory:
				items = body.inventory.get(item_type)
				for item in items:
					loot.append([item_type, item, body])
		return loot
	
	def removeItemsFromBodies(self):
		for body in self.corpses:
			body.clearInventory()
	