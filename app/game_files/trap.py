from app.game_files.gladiator import *
from numpy.random import choice as np_choice
from app.game_files.activity_feed import *
import random

class Trap:

	'''CONSTRUCTOR'''
	def __init__(self, damage, owner):
		self.damage = damage/100
		self.owner = owner
	
	def activateTrap(self, gladiator):
		reduced_health = gladiator.health - self.damage
		if reduced_health < 0.01:
			reduced_health = 0
		gladiator.health = reduced_health
		gladiator.arena.af.updateActivityFeed("%s TRIGGERED A TRAP" % gladiator.name, 
					"They triggered %s's trap!" % self.owner.name)
		if reduced_health == 0:
			gladiator.removeBody(self.owner, ActivityFeed.TRAPS)
			self.owner.increaseKillCount(gladiator)