import time
import random as r
from app.game_files.gladiator import *
from app.game_files.arena import *
import tkinter as tk
from app.game_files.nameslist import *
from app.game_files.bank import *
from fractions import Fraction
from app.game_files.tk_file import interfacePrintGrid
##visibly roughly 26 max particpants for tkinter

####################################
##Function prints information to tk#
####################################

def beginGames():
	arena1.start_button.destroy()
	continueGames()

def continueGames():
	while len(arena1.gladiators) > 1:
	
		arena1.nextTurn()
		###here for after each turn full instead
		#arena1.interfacePrintGrid()
		#arena1.window.after(TIMER, arena1.advance)#timer
		#arena1.window.mainloop()
	
	if len(arena1.gladiators) > 0:
		arena1.af.updateActivityFeed("WINNER", "%s wins!" % arena1.gladiators[0].name)
		for bet in arena1.bets_made:
			if bet.gladiator == arena1.gladiators[0]:
				arena1.betWon(bet)
	else:
		arena1.af.updateActivityFeed("GAME OVER", "So everyone died. There are no winners.")
	
	#reset button
	arena1.reset_button = tk.Button(arena1.activity_frame, text="New Bloodbath", 
			command=arena1.reset, width=20)
	arena1.reset_button.pack()
	
	arena1.window.mainloop()



a_w = 12
a_h = 12

max = a_w + a_h - 8
if max > 26:
	max = 26

no_glad = max-8


arena1 = Arena(a_w, a_h)

for _ in range(no_glad):
	arena1.addGladiator(Gladiator(r.choice(nameslist), r.randrange(99), 
			r.randrange(30,99), r.randrange(99)))



# NAME STRENGTH AGGRO SPEED
arena1.addGladiator(Gladiator("Honey", 100, 85, 60))
arena1.addGladiator(Gladiator("Harry", 100, 45, 80))
arena1.addGladiator(Gladiator("David", 50, 55, 80))
arena1.addGladiator(Gladiator("Eggy", 50, 8, 80))
arena1.addGladiator(Gladiator("Katie", 100, 100, 100))
arena1.addGladiator(Gladiator("Charlie", 50, 69, 70))
arena1.addGladiator(Gladiator("Sam", 50, 40, 60))
arena1.addGladiator(Gladiator("Shoopy", 100, 67, 89))
arena1.addGladiator(Gladiator("Limmy", 50, 50, 4))


arena1.start_button = tk.Button(arena1.activity_frame, text="Start Game", 
				command=beginGames, width=10)
arena1.start_button.pack()


arena1.prepareOdds()


interfacePrintGrid(arena1)
arena1.window.mainloop()



