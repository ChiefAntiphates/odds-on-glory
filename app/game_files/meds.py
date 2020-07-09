from app.game_files.gladiator import *
from numpy.random import choice as np_choice
from app.game_files.activity_feed import *
import random

class Meds:

	'''CONSTRUCTOR'''
	def __init__(self, heal, owner):
		self.heal = heal/100
		self.owner = owner
	