
class ActivityFeed:
	
	trap_header = "%(winner)s KILLED %(loser)s"
	TRAPS = [
[trap_header, "%(loser)s was killed by %(winner)s's trap!"]#trap message
	]
	
	self_header = "%s KILLED THEMSELVES"
	SELF_ATTACKS = [
[self_header, "%s tripped and fell off a cliff and died!"],
[self_header, "%s danced too good and went up in flames!"],
[self_header, "%s couldn't take it, they straight up killed themselves."]
	]
	
	af_kill = "af_kill"
	slayer_header = "%(winner)s KILLED %(loser)s"
	SLAYER_MESSAGES = [
[slayer_header,"%(winner)s killed %(loser)s!"],
[slayer_header, "%(winner)s slapped %(loser)s so hard that they died!"],
[slayer_header, "%(winner)s karate kicked %(loser)s right in the balls!"],
[slayer_header, "%(winner)s broke %(loser)s's heart, literally!"]
	]
	
	af_attack = "af_attack"
	attack_header = "%(attacker)s <span class='"+af_attack+"'>ATTACKING</span> %(defender)s"
	ATTACK_MESSAGES = [
[attack_header,"%(attacker)s started chasing after %(defender)s!"],
[attack_header,"%(defender)s is running from %(attacker)s! They have death in their eyes!"]
	]
	
	af_draw = "af_survive"
	draw_header =  "%(defender)s FOUGHT OFF %(attacker)s"
	DRAW_MESSAGES = [
[draw_header, "The battle between %(attacker)s and %(defender)s left them each bloodied, but alive."],
[draw_header, "%(defender)s fought off %(attacker)s! They each made it out with their lives."]	
	]
	
	af_loot = "af_loot"
	LOOT = "%s PICKED UP %s"
	LOOT_GIFT = "%s recieved the gift from %s."
	LOOT_CORPSE = "%s picked up the item from %s's corpse."
	
	af_trap = "af_trap"
	
	UNKNOWN = [
["Unknown %s death", "%s died"]
	]
	
	'''CONSTRUCTOR'''
	def __init__(self):
		self.activity = []
		
	def updateActivityFeed(self, header, message):
		self.activity.append([header, message])
		
	

		
		