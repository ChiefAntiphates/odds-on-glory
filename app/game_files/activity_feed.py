
class ActivityFeed:

#############################
##KILLS################
#############################
	af_kill = "af_kill"#Set css class
	trap_header = "%(winner)s <span class='"+af_kill+"'>KILLED</span> %(loser)s"
	TRAPS = [
[trap_header, "%(loser)s was killed by %(winner)s's trap!"]#trap message
	]
	
	self_header = "%s <span class='"+af_kill+"'>KILLED </span> themselves"
	SELF_ATTACKS = [
[self_header, "%s tripped and fell off a cliff and died!"],
[self_header, "%s danced too good and went up in flames!"],
[self_header, "%s couldn't take it, they straight up killed themselves."]
	]
	
	
	slayer_header = "%(winner)s <span class='"+af_kill+"'>KILLED</span> %(loser)s"
	SLAYER_MESSAGES = [
[slayer_header,"%(winner)s killed %(loser)s!"],
[slayer_header, "%(winner)s slapped %(loser)s so hard that they died!"],
[slayer_header, "%(winner)s karate kicked %(loser)s right in the balls!"],
[slayer_header, "%(winner)s broke %(loser)s's heart, literally!"]
	]
	
	
#############################
##ELIMINATION################
#############################
	elim_header = "%(winner)s <span class='"+af_kill+"'>ELIMINATED</span> %(loser)s"
	ELIM_MESSAGES = [
[elim_header,"%(winner)s eliminated %(loser)s!"],
[elim_header, "%(winner)s broke %(loser)s's jaw with a well-placed elbow!"]
	]
	
	self_elim_header = "%s <span class='"+af_kill+"'>ELIMINATED </span> themselves"
	SELF_ELIM_ATTACKS = [
[self_elim_header, "%s danced too good and went up in flames!"],
[self_elim_header, "%s couldn't take it, they collapsed!"]
	]
	
	elim_trap_header = "%(winner)s <span class='"+af_kill+"'>ELIMINATED</span> %(loser)s"
	ELIM_TRAPS = [
[elim_trap_header, "%(loser)s was eliminated by %(winner)s's trap!"]
	]
	
	
#############################
##ATTACKS################
#############################	
	af_attack = "af_attack"
	attack_header = "%(attacker)s <span class='"+af_attack+"'>ATTACKING</span> %(defender)s"
	ATTACK_MESSAGES = [
[attack_header,"%(attacker)s started chasing after %(defender)s!"],
[attack_header,"%(defender)s is running from %(attacker)s! They have death in their eyes!"]
	]


#############################
##SURVIVED################
#############################	
	af_draw = "af_survive"
	draw_header =  "%(defender)s <span class='"+af_draw+"'>SURVIVED</span> %(attacker)s"
	DRAW_MESSAGES = [
[draw_header, "The battle between %(attacker)s and %(defender)s left them each bloodied, but alive."],
[draw_header, "%(defender)s fought off %(attacker)s! They each made it out with their lives."]	
	]
	
	
#############################
##LOOT AND GIFTS################
#############################
	af_loot = "af_loot"
	LOOT = "%s <span class='"+af_loot+"'>PICKED UP</span> %s"
	LOOT_GIFT = "%s recieved the gift from %s."
	LOOT_CORPSE = "%s picked up the item from %s's corpse."
	
	af_trap = "af_trap"
	TRAP_SET = "%s <span class='"+af_trap+"'>SET A TRAP</span>"
	TRAP_TRIG = "%s <span class='"+af_trap+"'>TRIGGERED A TRAP</span>"
	UNKNOWN = [
["Unknown %s death", "%s died"]
	]
	
	
	'''CONSTRUCTOR'''
	def __init__(self):
		self.activity = []
		
	def updateActivityFeed(self, header, message):
		self.activity.append([header, message])
		
	