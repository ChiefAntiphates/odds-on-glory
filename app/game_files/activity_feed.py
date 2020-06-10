#import tkinter as tk

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
	
	slayer_header = "%(winner)s KILLED %(loser)s"
	SLAYER_MESSAGES = [
[slayer_header,"%(winner)s killed %(loser)s!"],
[slayer_header, "%(winner)s slapped %(loser)s so hard that they died!"],
[slayer_header, "%(winner)s karate kicked %(loser)s right in the balls!"],
[slayer_header, "%(winner)s broke %(loser)s's heart, literally!"]
	]
	
	attack_header = "%(attacker)s ATTACKING %(defender)s"
	ATTACK_MESSAGES = [
[attack_header,"%(attacker)s started chasing after %(defender)s!"],
[attack_header,"%(defender)s is running from %(attacker)s! They have death in their eyes!"]
	]
	
	draw_header =  "%(defender)s FOUGHT OFF %(attacker)s"
	DRAW_MESSAGES = [
[draw_header, "The battle between %(attacker)s sand %(defender)s left them each bloodied, but alive."],
[draw_header, "%(defender)s fought off %(attacker)s! They each made it out with their lives."]	
	]
	
	LOOT = "%s PICKED UP %s"
	LOOT_GIFT = "%s recieved the gift from %s."
	LOOT_CORPSE = "%s picked up the item from %s's corpse."
	
	UNKNOWN = [
["Unknown %s death", "%s died"]
	]
	
	'''CONSTRUCTOR'''##Lots of Tk throughout this file
	def __init__(self):
	#def __init__(self, activity_frame):
		#self.activity_frame = activity_frame
		self.activity = []
		
	def updateActivityFeed(self, header, message):
		self.activity.append([header, message])
		#self.tkStuff()
	
			
	'''
	###TK
	def tkStuff(self):
		tk.Label(self.activity_frame, text=self.activity[-1][1]+"\n", wraplength=200).pack(side="bottom")
		if "KILLED" in self.activity[-1][0]:
			tk.Label(self.activity_frame, text=self.activity[-1][0], wraplength=200, font='Calibri 10 bold', bg="#d4453b").pack(side="bottom")
		elif "FOUGHT OFF" in self.activity[-1][0]:
			tk.Label(self.activity_frame, text=self.activity[-1][0], wraplength=200, font='Calibri 10 bold', bg="#3180e8").pack(side="bottom")
		elif "PICKED UP" in self.activity[-1][0]:
			tk.Label(self.activity_frame, text=self.activity[-1][0], wraplength=200, font='Calibri 10 bold', bg="#37b859").pack(side="bottom")
		elif "TRAP" in self.activity[-1][0]:
			tk.Label(self.activity_frame, text=self.activity[-1][0], wraplength=200, font='Calibri 10 bold', bg="#a12dd6").pack(side="bottom")
		else:
			tk.Label(self.activity_frame, text=self.activity[-1][0], wraplength=200, font='Calibri 10 bold', bg="#ebb521").pack(side="bottom")
		
		activity_widgets = []
		for widget in self.activity_frame.winfo_children():
			activity_widgets.append(widget)
		
		if len(activity_widgets) > 16:
			activity_widgets[4].destroy()
			activity_widgets[5].destroy()
		self.activity_frame.update()
		
	'''	
		
		
		