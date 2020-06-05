import random
from tile import *
from gladiator import *
from activity_feed import *
from numpy.random import choice as np_choice
from tkinter import messagebox as tkalert

class Battle:
	
	'''CONSTRUCTOR'''
	def __init__(self, attacker, defender, tile, arena):
		self.attacker = attacker
		self.defender = defender
		self.tile = tile
		self.final_message="final message"
		self.arena = arena
		self.winner = None
		self.loser = None
		self.defence_damage = None
		self.offence_damage = None

		
		self.notifyAttack()
		
		
	
	
	def notifyAttack(self):
		##Attacker messages need to be put somewhere
		#attacker_message_full = random.choice(list(ActivityFeed.ATTACK_MESSAGES))
		#attacker_message = attacker_message_full[1] % {'attacker': self.attacker.name, 'defender': self.defender.name}
		#header = attacker_message_full[0] % {'attacker': self.attacker.name, 'defender': self.defender.name}
		#self.arena.af.updateActivityFeed(header, attacker_message)
		self.arena.active_battles.append(self)
		self.attacker.setBattle(self)
		self.defender.setBattle(self)
	
	
	def basic_fight(self):
		if not(self.attacker.alive) or not(self.defender.alive):
			self.attacker.endBattle(self)
			self.defender.endBattle(self)
			self.arena.active_battles.remove(self)
		
		else:
			print("\nBATTLE STATS")
			draw, attack, defend = 0.6, 0.21, 0.19
			
			print("Base values: %s" % [attack, defend, draw])
			
			
			#################################
			#Health probability modification#
			#################################
			attacker_health_diff = attack - (self.attacker.health * attack)
			defender_health_diff = defend - (self.defender.health * defend)
			attack = (self.attacker.health * attack) + defender_health_diff
			defend = (self.defender.health * defend) + attacker_health_diff
			
			print("Healths: %s" %[self.attacker.health, self.defender.health])
			print("After health difference: %s" % [attack, defend, draw])
			
			
			
			
			print("Attack str: %s, Defend str: %s" % (self.attacker.strength, self.defender.strength))
			
			###################################
			#Strength probability modification#
			###################################
			attack_strength_mod = ((draw-0.05)/2) * self.attacker.strength
			defend_strength_mod = ((draw-0.05)/2) * self.defender.strength
			draw = draw - defend_strength_mod - attack_strength_mod
			attack += attack_strength_mod
			defend += defend_strength_mod
			
			
			print("After strength difference: %s" % [attack, defend, draw])
			
			
			
			
			#################################
			#Weapon probability modification#
			#################################
			#Modify draw AND opponent if weapon
		
			print("%s v %s" % (self.attacker.name, self.defender.name))
			print(attack, defend, draw)
			############
			#Run battle#
			############
			self.offence_damage = attack
			self.defence_damage = defend
			np_choice([self.noWin, self.attackerWin, self.defenderWin], 1, 
											p=[draw, attack, defend])[0]()
			try:
				print(self.winner.name)
			except AttributeError as e:
				print("draw")
			print("\n")
			self.attacker.endBattle(self)
			self.defender.endBattle(self)
			
			self.arena.active_battles.remove(self)
	
	
	
	def noWin(self):
		draw_message_full = random.choice(list(ActivityFeed.DRAW_MESSAGES))
		header = draw_message_full[0] % {'defender': self.defender.name, 'attacker': self.attacker.name}
		draw_message = draw_message_full[1] % {'attacker': self.attacker.name, 'defender': self.defender.name}
		self.arena.af.updateActivityFeed(header, draw_message)
		
		self.takeDamage(self.offence_damage, self.defender)
		self.takeDamage(self.defence_damage, self.attacker)
		
	def attackerWin(self):
		self.winner = self.attacker
		self.loser = self.defender
		
		self.takeDamage(self.defence_damage, self.attacker)
		
		self.finishBattleKill()
	
	def defenderWin(self):
		self.winner = self.defender
		self.loser = self.attacker
		
		self.takeDamage(self.offence_damage, self.defender)
		
		self.finishBattleKill()
	
	
		
	def finishBattleKill(self):
		self.winner.increaseKillCount(self.loser)
		self.loser.removeBody(self.winner, ActivityFeed.SLAYER_MESSAGES)
	
	
	def takeDamage(self, damage_type, damage_taker):
		lower = damage_type * 0.8
		upper = damage_type * 1.2
		health_reduction = random.choice([lower, upper, damage_type])
		new_health = damage_taker.health - (damage_taker.health * health_reduction)
		if new_health < 0.01:
			new_health = 0.01
		damage_taker.setHealth(new_health)
		
	