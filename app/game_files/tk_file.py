import time
import random as r
from app.game_files.gladiator import *
from app.game_files.arena import *
import tkinter as tk
from app.game_files.nameslist import *
from app.game_files.bank import *
from fractions import Fraction

def interfacePrintGrid(arena1):


	def displayGladInfo(glad, alive):
		##just to close window these mini funcs
		def prepareBet(glad):
			glad_win.destroy()
			arena1.prepareBet(glad)
		def sendGladiatorTrap(glad):
			glad_win.destroy()
			arena1.sendGladiatorTrap(glad)
			
		glad_win = tk.Toplevel(arena1.window)
		glad_win.minsize(220,175)
		tk.Label(glad_win, text=glad.name, font='Calibri 10 bold').grid(column=0, row=0)
		if alive:
			tk.Label(glad_win, text=arena1.odds_on[glad][2], font='Calibri 10 bold').grid(column=1, row=0)
			tk.Button(glad_win, text="Place Bet", 
				command=partial(prepareBet, glad), width=10).grid(column=2, row=0, padx=5)
			tk.Button(glad_win, text="Send Trap", 
				command=partial(sendGladiatorTrap, glad), width=10).grid(column=2, row=1, padx=5)
		
			tk.Label(glad_win, text="Health: %s/100" % str(glad.health*100)[:3].replace(".","")).grid(column=0, row=1)
		else:
			tk.Label(glad_win, text="Killed by: %s" % glad.killed_by.name).grid(column=0, row=1)
		tk.Label(glad_win, text="Kills: %s" % str(glad.kill_count)[:3]).grid(column=0, row=2)
		tk.Label(glad_win, text="Strength: %s/10" % str(glad.strength*10)[:3]).grid(column=0, row=3)
		tk.Label(glad_win, text="Aggression: %s/10" % str(glad.aggro*10)[:3]).grid(column=0, row=4)
		tk.Label(glad_win, text="Speed: %s/10" % str(glad.base_speed*10)[:3]).grid(column=0, row=5)
		tk.Label(glad_win, text="Current State: %s" % glad.state).grid(column=0, row=5)
		tk.Label(glad_win, text="Victims:").grid(column=2, row=2)
		temp_count = 2
		for victim in glad.kills:
			temp_count += 1
			tk.Label(glad_win, text=victim.name).grid(column=2, row=temp_count)
		
	def getGladiatorInfo(gladiator, alive):
		gladiator_info = gladiator.name
		if alive:
			gladiator_info += " | HP: " + str(round(gladiator.health*100))
			gladiator_info += " | " + arena1.odds_on[gladiator][2]#remove
		gladiator_info += " | Kills: " + str(gladiator.kill_count)
		if alive:
			gladiator_info += " | " + gladiator.state
		return gladiator_info
	
	widgets_to_delete = []
	for widget in arena1.frame.winfo_children():
		widgets_to_delete.append(widget)#create array to delete old widgets
		
	for row in arena1.grid:
		for tile in row:
			if tile.hostile:
				colour = "#9c3427"
			else:
				colour = "#89a4c4"
			canvas = tk.Canvas(arena1.frame, bg=colour, width=50, height=50)
			canvas.grid(row=tile.y_pos, column=tile.x_pos)
			canvas.create_text(25, 25,text=tile.toString())
			if tile.trap_present and not tile.hostile:
				canvas.create_text(12, 7,text=tile.trap.owner.initial, font='Calibri 9 bold', fill="#a12dd6")
			if len(tile.corpses) > 0:
				canvas.create_text(25, 45,text="|".join([body.initial for body in tile.corpses]), font='Calibri 8 bold', fill = "#52061a")
			canvas.update()
			
	for widget in widgets_to_delete: #Clear the grid beneath to avoid backlog
		widget.destroy()
		
	####################################
	
	if (arena1.duration % 48 < 40) and (arena1.duration % 48 >= 12):
		arena1.datetext.configure(text = "Day %s" % ((arena1.duration // 48)+1))
	elif (arena1.duration % 48 < 40):
		arena1.datetext.configure(text ="Night %s" % (arena1.duration // 48))
	else:
		arena1.datetext.configure(text ="Night %s" % ((arena1.duration // 48)+1))
	
	timetext_var = str((arena1.duration % 48)/2).replace(".0",":00")
	timetext_var = timetext_var.replace(".5",":30")
	if len(timetext_var) < 5:
		timetext_var = "0"+timetext_var
	arena1.timetext.configure(text = timetext_var)

	####################################
	
	

	for widget in arena1.gladiator_frame.winfo_children():
		widget.destroy()
		
	tk.Label(arena1.gladiator_frame, text="Gladiators").pack()
	for gladiator in arena1.gladiators:
		gladiator_info = getGladiatorInfo(gladiator, True)
		tk.Button(arena1.gladiator_frame, text=gladiator_info, 
			command=partial(displayGladInfo, gladiator, True), width=36).pack()
			
	for widget in arena1.dead_gladiator_frame.winfo_children():
		widget.destroy()
	tk.Label(arena1.dead_gladiator_frame, text="Dead Gladiators").pack()
	for gladiator in arena1.dead_gladiators:
		gladiator_info = getGladiatorInfo(gladiator, False)
		tk.Button(arena1.dead_gladiator_frame, text=gladiator_info, 
			command=partial(displayGladInfo, gladiator, False), width=18).pack()
			
			
	################################
	for widget in arena1.battles_frame.winfo_children()[1:]:
		widget.destroy()
	for battle in arena1.active_battles:
		tk.Label(arena1.battles_frame, 
			text="%s vs %s" % (battle.attacker.name, battle.defender.name)).pack() 