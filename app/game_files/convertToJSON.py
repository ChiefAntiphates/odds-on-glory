import json

def pushInfoToJSON(arena):
	arena_info = {
		"width": arena.width,
		"height": arena.height,
		"duration": arena.duration,
		"active": arena.active,
		"tile_rows": [],
		"gladiators": [],
		"dead_gladiators": [],
		"runners": [],
		"battles": [],
		"activity_log": arena.af.activity
		}
	
	for tile_row in arena.grid:
		tile_row_ref = {"tiles": []}
		tile_row_ref["row_no"] = tile_row[0].y_pos
		for tile in tile_row:
			json_tile = {}
			json_tile["x_co"] = [tile.x_pos]
			json_tile["y_co"] = [tile.y_pos]
			json_tile["occupant_initials"] = [x.initial for x in tile.occupants]	
			json_tile["occupant_names"] = [x.name for x in tile.occupants]
			json_tile["corpse_initials"] = [x.initial for x in tile.corpses]	
			json_tile["corpse_names"] = [x.name for x in tile.corpses]
			json_tile["hostile"] = tile.hostile
			if tile.trap_present:
				json_tile["trap"] = tile.trap.owner.name
			else:
				json_tile["trap"] = False
			tile_row_ref["tiles"].append(json_tile)
		arena_info["tile_rows"].append(tile_row_ref)
	
	for glad in arena.gladiators:
		json_glad = {}
		json_glad["name"] = glad.name
		json_glad["initial"] = glad.initial
		json_glad["odds"] = arena.odds_on[glad][2]
		json_glad["strength"] = glad.strength
		json_glad["speed"] = glad.base_speed
		json_glad["aggro"] = glad.base_aggro
		json_glad["health"] = round(glad.health,2)
		json_glad["kill_count"] = glad.kill_count
		json_glad["kills"] = [x.name for x in glad.kills]
		json_glad["state"] = glad.state
		arena_info["gladiators"].append(json_glad)
		
	for glad in arena.dead_gladiators:
		json_dead = {}
		json_dead["name"] = glad.name
		json_dead["initial"] = glad.initial
		json_dead["kill_count"] = glad.kill_count
		json_dead["kills"] = [x.name for x in glad.kills]
		json_dead["slayer"] = glad.killed_by.name
		arena_info["dead_gladiators"].append(json_dead)
	
	for runner in arena.runners:
		json_runner = {}
		json_runner["name"] = runner.name
		json_runner["initial"] = runner.initial
		json_runner["target"] = runner.target_gladiator.name
		arena_info["runners"].append(json_runner)
	
	for battle in arena.active_battles:
		json_battle = {}
		json_battle["attacker"] = battle.attacker.name
		json_battle["defender"] = battle.defender.name
		arena_info["battles"].append(json_battle)
	
	json_arena = json.dumps(arena_info)
	return json_arena