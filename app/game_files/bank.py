from fractions import Fraction

class Bet:
	'''CONSTRUCTOR'''
	def __init__(self, arena, gladiator, bet, punter_id):
		self.odds_info = arena.odds_on[gladiator]
		numer = self.odds_info[0]
		denom = self.odds_info[1]
		
		self.arena = arena
		self.gladiator = gladiator
		
		self.bet = int(bet)
		self.betReturn = calculateBetReturn(numer, denom, self.bet)
		self.punter_id = punter_id

def calculateOdds(gladiators):
	if len(gladiators) == 1:
		return {gladiators[0]: [0, 0, "WIN"]}
	elif len(gladiators) == 0:
		return []
	standard_odds = 100/len(gladiators)
	glads_odds = [[gladiator, standard_odds] for gladiator in gladiators]
	
	##Largest modifier is strength, then modifier weight is smallest share to avoid negatives
	glads_odds = traitOddsModifiers(glads_odds, "strength", 100/(len(gladiators)+1))
	glads_odds = traitOddsModifiers(glads_odds, "health", min([item[1] for item in glads_odds]))
	glads_odds = traitOddsModifiers(glads_odds, "speed", min([item[1] for item in glads_odds]))
	
	final_gladiator_odds = {}
	for glad, share in glads_odds:
		share = str(Fraction(share*3, 100))
		if share == "0":
			share = "1/500"
		elif "/" not in share:
			share = share+"/1"
		denom, numer = share.split("/")
		#final_gladiator_odds.append([glad, int(numer), int(denom), numer+"/"+denom])
		final_gladiator_odds[glad] = [int(numer), int(denom), numer+"/"+denom]
	
	return final_gladiator_odds

def traitOddsModifiers(glads_odds, attribute, modifier):
	total = 0.1
	for glad, share in glads_odds:
		total += glad.getAttribute(attribute)
	average = total/len(glads_odds)
	
	new_glads_odds = []
	
	for glad, share in glads_odds:
		score = glad.getAttribute(attribute)
		if score >= average:
			multiplier = (score/average)-1
			addition = modifier*multiplier
			share += addition
		else:
			multiplier = 1-(score/average)
			subtraction = modifier*multiplier
			share -= subtraction
		new_glads_odds.append([glad, round(share)])
	return new_glads_odds

def calculateBetReturn(numer, denom, bet):
	return round((numer/(denom/bet))) + bet