import time
import random as r
from numpy.random import choice as np_choice
from app.game_files.tile import *
from app.game_files.battle import *
from app.game_files.trap import *
from app.game_files.activity_feed import *

class Gladiator:
	
	MOVE = "Roaming"
	FIGHT = "In Battle"
	HUNT = "Hunting"
	TRAP = "Laying Trap"
	HEAL = "Healing and Resting"
	PRAY = "Praying"
	
	I_TRAPS = "A TRAP"
	I_WEAPONS = "A WEAPON"
	I_MEDICINE = "MEDICINE"
	
	
	
	'''CONSTRUCTOR'''
	def __init__(self, name, strength, aggro, speed):
		self.name = name
		
		#Gladiator Base Attributes
		self.strength = strength/100
		self.base_speed = speed/100
		self.base_aggro = aggro/100
		
		
		#Gladiator Modifier Attributes
		self.speed = self.base_speed
		self.aggro = self.base_aggro
		self.health = 1.0
		
		self.alive = True
		self.allies = []
		self.state = Gladiator.MOVE
		fname = name.split(" ")[0]
		self.initial = fname[0].upper() + fname[1:3].lower()
		self.arena = None
		self.x_pos = None
		self.y_pos = None
		self.tile = None
		self.prev_tile = None
		self.inBattle = False
		self.kill_count = 0
		self.kills = []
		self.killed_by = None
		self.battles = []
		self.possibleTileMoves = []
		self.consecutive_hunt = 0
		self.turn_delay = 0
		self.delayed_fun = None
		
		self.id = id(self)
		##self.owner = FOR WHEN WE GET SERIOUS
		
		#Inventory
		self.inventory={
			Gladiator.I_TRAPS: [],
			Gladiator.I_WEAPONS: [],
			Gladiator.I_MEDICINE: []
		}
		
		#Describe time it should take to complete actions
		#ie. wait x turns, then on x+1 action is carried out
		self.TD_FUN = {
			self.placeTrap: [3, Gladiator.TRAP]
		}
		
		
		
	def setArena(self, arena):
		self.arena = arena
	
	
	def setPosition(self, x_co, y_co):
		self.x_pos = x_co
		self.y_pos = y_co
		self.tile = self.arena.grid[self.y_pos][self.x_pos]
		self.prev_tile = self.tile
		
		
	def executeTurn(self):
		self.statChanges()
		if self.alive:
			if (len(self.battles) > 0) and not self.inBattle:
				self.inBattle = True #Assigning here to have battles last over 2 turns
			elif self.inBattle:
				self.battles[0].basic_fight()
			elif self.turn_delay > 0:
				self.turnDelay()
			else:
				if len(self.tile.getItemsFromBodies()) > 0:
					self.getLoot()
				action_prob = self.assessOptions()
				chosen_func = np_choice([i[0] for i in action_prob],1, p=[i[1] for i in action_prob])[0]
				if chosen_func in self.TD_FUN:
					self.turn_delay = self.TD_FUN[chosen_func][0]
					self.delayed_fun = chosen_func
					self.state = self.TD_FUN[chosen_func][1]
				else:
					chosen_func()
					
			
	
	def removeBody(self, slayer, cod): #cod = cause of death
		self.tile.removeGladiator(self)
		self.tile.corpses.append(self)
		self.arena.gladiators.remove(self)
		self.arena.dead_gladiators.append(self)
		self.killed_by = slayer	
		self.alive = False
		
		msg_choice = r.choice(cod)
		if cod in [ActivityFeed.SLAYER_MESSAGES, ActivityFeed.TRAPS]:
			self.arena.af.updateActivityFeed(
				msg_choice[0] % {'winner': slayer.name, 'loser': self.name},
				msg_choice[1] % {'winner': slayer.name, 'loser': self.name})
		else:
			self.arena.af.updateActivityFeed(msg_choice[0] % self.name, msg_choice[1] % self.name)
			
		
	def detectNearbyGladiators(self):
		success = False
		nearby_tiles = list(self.arena.getTileSurroundings(self.tile))
		occupied_tiles = []
		lowest_health = 1.0
		low_health_tile = None
		for tile in nearby_tiles:
			if tile.occupied:
				occupied_tiles.append(tile)
				success = True
				if len(tile.occupants) == 1:
					lowest_health = tile.occupants[0].health
					low_health_tile = tile
		return success, occupied_tiles, lowest_health, low_health_tile
	
	
	def setBattle(self, battle):
		self.battles.append(battle)
		self.state = Gladiator.FIGHT
		self.turn_delay = 0
		self.delayed_fun = None
	
	def endBattle(self, battle):
		self.battles.remove(battle)
		if len(self.battles) == 0:
			self.inBattle = False
	
	def setHealth(self, health):
		self.health = health
	
	def turnDelay(self):
		if self.turn_delay == 1:
			self.delayed_fun()
			self.delayed_fun = None
			self.turn_delay = 0
		else:
			self.turn_delay -= 1
	
	def getLoot(self):
		loot = self.tile.getItemsFromBodies()
		for item in loot:
			self.arena.af.updateActivityFeed(ActivityFeed.LOOT % (self.name, item[0]), 
				ActivityFeed.LOOT_CORPSE % (self.name, item[2].name))#Updating activity log
			item[1].owner = self
			self.inventory[item[0]].append(item[1])
		self.tile.removeItemsFromBodies()
	
	####################
	##ACTION FUNCTIONS##
	####################
	
	def attack(self):
		victims = list(self.tile.occupants)
		victims.remove(self)
		self.inBattle = True
		Battle(self, r.choice([x for x in victims if x not in self.allies]), self.tile, self.arena)
		self.state = Gladiator.FIGHT
		
		
	#change so that enemies nearby changes probabilities
	def hunt(self):
		success, occupied_tiles, low_health, low_tile = self.detectNearbyGladiators()
		if self.health > low_health:
			self.moveToTile(low_tile)
		else:
			self.moveToTile(r.choice(occupied_tiles))
		self.state = Gladiator.HUNT
		
		##Attack in same turn if higher speed than victims
		victims = list(self.tile.occupants)
		try:
			victims.remove(self)
			
			highest_speed = True
			for victim in victims:
				if (self.speed <= victim.speed):
					highest_speed = False
				if victim in self.allies:
					victims.remove(victim)
			if highest_speed and len(victims)>0:
				self.attack()
		except ValueError as e:
			print(e)
	
	
	def placeTrap(self):
		trap = self.inventory[Gladiator.I_TRAPS][0]
		self.tile.setTrapToTile(trap)
		self.inventory[Gladiator.I_TRAPS].remove(trap)
		self.arena.af.updateActivityFeed("%s SET A TRAP" % self.name, 
													"They set down a trap")
		
	def fatalAccident(self):
		self.removeBody(self, ActivityFeed.SELF_ATTACKS)
		self.state = Gladiator.FIGHT
	
	
	def pray(self):
		print("%s decided to pray." % self.name)
		self.state = Gladiator.PRAY
		
		
	def moveToRandomTile(self):
		try:
			tile_list = list(self.arena.getTileSurroundings(self.tile))
			for tile in tile_list:
				if tile.occupied:
					tile_list.remove(tile)
				if self.prev_tile == tile:
					tile_list.remove(tile)
					
			tile = r.choice(tile_list)
			self.moveToTile(tile)
		except IndexError as e:
			print("%s can't move anywhere!")
		self.state = Gladiator.MOVE
		
		
	#######################################################
	#Assess all options that are available - probabilities# 
	#######################################################
	def assessOptions(self):
		gladiators_nearby, tiles, low_health, low_tile = self.detectNearbyGladiators()
		
		action_prob = []
		remaining_prob = 1.0
		
		###################
		#ATTACKING/HUNTING#
		###################
		##Use same probabilities for attack and hunt
		attack_chance = remaining_prob * self.aggro #Aggression modifier
		if self.health > low_health: #Health difference motivation
			attack_chance += (self.health - low_health)
		elif self.aggro < 0.95 and self.health < 0.8: #Reduce if lower health unless super aggro
			attack_chance = attack_chance * self.health 
		#if (self.arena.duration < 14) and self.aggro < 0.9:#and self.agro < 0.9 ##V. unlikely to attack in starting hours
		#	attack_chance = attack_chance * 0.1#DISABLES ATTACK EARLY
		if attack_chance > 0.98:
			attack_chance = 0.98
		if (self.state == Gladiator.FIGHT and self.aggro < 0.95):
			attack_chance = 0.01

		#If enemy in same tile -> attack chance#
		if ((len(self.tile.occupants) > 1) and 
				len([occ for occ in self.tile.occupants if (occ not in self.allies) and (occ != self)])>0):
			if self.state == Gladiator.HUNT:##Always attack after successful hunt
				action_prob.append([self.attack, remaining_prob])
				remaining_prob = remaining_prob - remaining_prob
			else:	
				action_prob.append([self.attack, attack_chance])
				remaining_prob = remaining_prob - attack_chance
			#if previous state == hunt
		
		#If gladiators are nearby -> hunt chance#
		elif gladiators_nearby: #can't have attack and hunt in same selection
			action_prob.append([self.hunt, attack_chance])
			remaining_prob = remaining_prob - attack_chance
		
		'''Comment in updated probabilities throughout'''
		
		##Place trap
		if (len(self.inventory[Gladiator.I_TRAPS]) > 0) and (self.arena.duration > 20) and not(self.tile.edge):
			action_prob.append([self.placeTrap, remaining_prob * 0.35])
			remaining_prob = remaining_prob - (remaining_prob * 0.35)
		
		##Fatal accident
		action_prob.append([self.fatalAccident, remaining_prob * 0.0004])
		remaining_prob = remaining_prob - (remaining_prob * 0.0004)
		
		##Random move (final condition)
		if len(list(self.arena.getTileSurroundings(self.tile))) > 0:
			action_prob.append([self.moveToRandomTile, remaining_prob])
		else:
			action_prob.append([self.pray, remaining_prob])
		return action_prob
	#######################################################
	#############END PROBABILITY ASSESSMENT################
	#######################################################
	
	
	
	def moveToTile(self, move_tile):
		self.prev_tile = self.tile
		self.tile.removeGladiator(self)
		self.setPosition(move_tile.x_pos, move_tile.y_pos)
		self.arena.grid[move_tile.y_pos][move_tile.x_pos].setGladiatorToTile(self)
	
		
		
	#Put further health recovery conditions here
	def statChanges(self):
		##HEALTH REDUCTION DUE TO HOSTILE AREA
		if self.tile.hostile and self.prev_tile.hostile:
			self.health -= 0.2

		#INCREASE AGGRO GRADUALLY IF NOT FOUGHT IN LONG TIME
		if self.state == Gladiator.FIGHT:
			self.aggro = self.base_aggro
		else:
			if self.aggro < 0.98:
				self.aggro += 0.01 
		
		#KILL IF HEALTH IS ZERO
		if self.health < 0.009:
			self.removeBody(self, ActivityFeed.UNKNOWN)
			
		#SPEED ADJUSTMENT
		self.speed = self.base_speed
		if self.state == Gladiator.HUNT:
			self.consecutive_hunt += 0.8
			self.speed += (self.consecutive_hunt/10) #is this too much extra speed?
		elif self.consecutive_hunt > 0:
			self.consecutive_hunt = 0
		#Adjust speed with health, maybe sub this for fatigue/energy
		self.speed = self.speed * self.health
		
		#if fully rested or fed etc.
		if self.health < 0.8:
			self.health += 0.005
	
	
	def increaseKillCount(self, enemy):
		if not(type(enemy) is Runner):		
			self.kill_count += 1
			self.kills.append(enemy)
		else:
			print("killed a runner")
		
	def clearInventory(self):
		self.inventory={
			Gladiator.I_TRAPS: [],
			Gladiator.I_WEAPONS: [],
			Gladiator.I_MEDICINE: []
		}
	
	
	def moveTowardsTargetTile(self, target):
		if self.tile != target:#does not account for obstacles in path
			if (self.x_pos > target.x_pos) and (self.y_pos > target.y_pos):
				self.moveToTile(self.arena.grid[self.y_pos-1][self.x_pos-1])
			elif (self.x_pos < target.x_pos) and (self.y_pos < target.y_pos):
				self.moveToTile(self.arena.grid[self.y_pos+1][self.x_pos+1])
			elif (self.x_pos < target.x_pos) and (self.y_pos > target.y_pos):
				self.moveToTile(self.arena.grid[self.y_pos-1][self.x_pos+1])
			elif (self.x_pos > target.x_pos) and (self.y_pos < target.y_pos):
				self.moveToTile(self.arena.grid[self.y_pos+1][self.x_pos-1])
			elif (self.x_pos < target.x_pos):
				self.moveToTile(self.arena.grid[self.y_pos][self.x_pos+1])
			elif (self.y_pos < target.y_pos):
				self.moveToTile(self.arena.grid[self.y_pos+1][self.x_pos])
			elif (self.x_pos > target.x_pos):
				self.moveToTile(self.arena.grid[self.y_pos][self.x_pos-1])
			else:
				self.moveToTile(self.arena.grid[self.y_pos-1][self.x_pos])
		
		
	def getAttribute(self, attribute):
		if attribute == "strength":
			return self.strength
		elif attribute == "aggro":
			return self.aggro
		elif attribute == "speed":
			return self.base_speed
		elif attribute == "health":
			return self.health
		else:
			return None

class Runner(Gladiator):
	def __init__(self, name, strength, aggro, speed, target_gladiator, item):
		##sort out how arena handles display of Runners
		super().__init__(name, strength, aggro, speed)
		self.target_gladiator = target_gladiator
		self.name = self.target_gladiator.name + "'s Runner: " + self.name
		self.initial = "R:" + self.target_gladiator.initial
		self.mission_achieved = False
		
		#add in form ["type", object]
		self.inventory[item[0]].append(item[1])
		self.item = item
		
		self.exit = None
		self.allies = [target_gladiator]
		target_gladiator.allies.append(self)
	
		self.health = 0.25 #Reduced health
	
	
	def executeTurn(self):
		if self.alive:
			if (len(self.battles) > 0) and not self.inBattle:
				self.inBattle = True #Assigning here to have battles last over 2 turns
			elif self.inBattle:
				self.battles[0].basic_fight()
				
			elif self.mission_achieved:
				if self.tile == self.exit:
					self.tile.removeGladiator(self)
					self.arena.runners.remove(self)
				else:
					self.moveTowardsTargetTile(self.exit)
			elif not self.target_gladiator.alive:
				self.mission_achieved = True
				self.exit = r.choice(self.arena.edge_tiles)
			else:
				self.moveTowardsTargetTile(self.target_gladiator.tile)
				if self.tile == self.target_gladiator.tile:
					self.passGift()
					self.mission_achieved = True
					self.exit = r.choice(self.arena.edge_tiles)
	
	
	def passGift(self):
		self.item[1].owner = self.target_gladiator
		self.target_gladiator.inventory[self.item[0]].append(self.item[1])
		self.inventory[self.item[0]].remove(self.item[1])
		
		self.arena.af.updateActivityFeed(ActivityFeed.LOOT % (self.target_gladiator.name, self.item[0]), 
			ActivityFeed.LOOT_GIFT % (self.target_gladiator.name, self.name))#Updating activity log
	
	
	def removeBody(self, slayer, cod): #cod = cause of death
		self.tile.removeGladiator(self)
		self.tile.corpses.append(self)
		self.arena.runners.remove(self)
		self.killed_by = slayer
		self.alive = False
		
		msg_choice = r.choice(cod)
		if cod in [ActivityFeed.SLAYER_MESSAGES, ActivityFeed.TRAPS]:
			self.arena.af.updateActivityFeed(
				msg_choice[0] % {'winner': slayer.name, 'loser': self.name},
				msg_choice[1] % {'winner': slayer.name, 'loser': self.name})
		else:
			self.arena.af.updateActivityFeed(msg_choice[0] % self.name, msg_choice[1] % self.name)
		
		
		