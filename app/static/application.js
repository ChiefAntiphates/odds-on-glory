//var global_glad_list = [];
var global_activity_feed = [];
var global_dead_gladiators = [];

$(document).ready(function(){
	console.log(game_code)
    //connect to the socket server.
    var socket = io.connect('https://' + document.domain + ':' + location.port + game_code);
    var arena_active = json_arena.active;
	//console.log('{{ game_code|safe }}');
	//Upon connecting build arena incase missed the update
	initArenaGlads(json_arena)
	
	
	if (arena_active === true) {
		let time_hold = document.getElementById("overlay");
		time_hold.remove();
	}
	
	
	//Add gladiator button - removed at start of betting phase
	if (logged_in === true){
		if ((arena_active == false) && (Object.keys(gladiator_options).length > 0)){
			
			//gladiator_options | CURRENTLY RELIES ON UNIQUE NAME
			let selbut = "";
			selbut += "<select id='glad_select'>";
			var no_glads = Object.keys(gladiator_options).length;
			for (i=0; i<no_glads; i++){
				selbut += "<option value='"+gladiator_options[i].id+"'>"+gladiator_options[i].name+"</option>";
			}
			selbut += "</select>";
			
			document.getElementById("add_glad_but").innerHTML = selbut;
			
			let button = document.createElement("button");
			button.innerHTML = "Add Gladiator";
			document.getElementById("add_glad_but").appendChild(button)
			button.addEventListener("click", function() {
				let sel = document.getElementById("glad_select")
				let sel_glad_id = sel.options[sel.selectedIndex].value;
				//let glad = gladiator_options[sel.selectedIndex];
				console.log(gladiator_options);
				
				for (gladiator in gladiator_options){
					if (Number(gladiator_options[gladiator].id) === Number(sel_glad_id)){
						console.log("yay");
						var glad = gladiator_options[gladiator];
						break;
					}
				}
				console.log(glad);
				swal({
					title: "Submit " + glad.name +" to Arena?",
					text: "If they die they're dead forever!",
					icon: "warning",
					buttons: [
						'No, perhaps not...',
						'Yes, let them prove themselves!'
					]
				})
				.then((isConfirm) => {
					if (isConfirm) {
						if ((arena_active == false)){
							console.log(glad);
							$.ajax({
								type : "POST",
								url : '/add_gladiator_to_arena',
								data: {gladiator: JSON.stringify(glad), game_code: game_code}//This is how to send vars to flask
							});
							swal({
								title: "Gladiator Entered",
								text: glad.name+" has entered the arena...",
								icon: "success",
								timer: 3000
							});
							sel.remove(sel.selectedIndex);
							sel.selectedIndex = 0;
						}else {
							console.log("outta time!!");
						}
					} else {
						console.log("Gladiator not entered");
					}
				});
			});
		}
	}//END add gladiator button
	
	

	
	
	
	//SOCKET RESPONSES
	
	//Socket response to a new gladiator added
	socket.on('gladiatoradding', function(msg) {
		var gladiatoradding_arena = JSON.parse(msg.json_obj);
		let glad_view = document.getElementById("glad_info");
		var g_v_content = ""
		for (var gladiator in gladiatoradding_arena.gladiators) {
			var glad_name = gladiatoradding_arena.gladiators[gladiator].name;
		
			g_v_content += "<p>" + glad_name + "</p>";
			g_v_content += "<br>";
		}
		glad_view.innerHTML = g_v_content;
		
		let timer = document.getElementById("over_text");
		timer.innerHTML = "Time left to add gladiators:<br>"+msg.timer;
	});
	
	
	//Update countdown in betting phase
	socket.on('arenabetting', function(msg) {
		let timer = document.getElementById("over_text");
		timer.innerHTML = "BETTING PHASE<br>Game begins in:<br>"+msg.timer;
		console.log(msg.timer);
		if (msg.timer === 0){
			let time_hold = document.getElementById("overlay");
			time_hold.remove();
		}
		
	});
	
	
	//Socket response to initialise the betting phase
	socket.on('arenainitial', function(msg) {
		arena_active = true;
		elem = document.getElementById("add_glad_but")
		elem.parentNode.removeChild(elem);//Remove add gladiator button
		var arena_initial_in = JSON.parse(msg.json_obj);
		initArenaGlads(arena_initial_in)
	});
	
	
	//Socket response to game finishing //Remove buttons etc.
	socket.on('arenafinish', function(msg) {
		if (logged_in === true) {
			$.ajax({ //Here we will also sell or return the winning gladiator
				type : "POST",
				url : '/finish_game',
				data: {game_code: game_code, winner: msg.winner},//Submit the final gladiator
				success: function(data) { //Update money on screen
					var money_display = document.getElementById("money_display");
					money_display.innerHTML = "Money: " + data;
				}
			});
		}
	});
	
	

    //Upon Socket arena update event
    socket.on('arenaupdate', function(msg) {
		var arena = JSON.parse(msg.json_obj);
		//console.log(arena);
		
		
		//Update tiles//NOTE: Convert to canvas at some point
        var table = document.getElementById("arena_grid");
		for (var tile_row in arena.tile_rows) {
			for (var tiles_parser in arena.tile_rows[tile_row].tiles){
				var tile = arena.tile_rows[tile_row].tiles[tiles_parser]
				var table_td = table.rows[tile_row].cells[tiles_parser]
				table_td.innerHTML = tile.occupant_initials.join("<br>");
				if (tile.corpse_present === true){
					table_td.style.backgroundImage = "url('"+cross_img_url+"')";
				}
				if  (tile.hostile === true) { //if hostile
					table_td.style.backgroundColor = "#821111"; 
					table_td.style.outline = null;
				} else if (tile.trap !== false){
					table_td.style.outline = "3px dashed purple";
				}else{
					table_td.style.outline = null;
				}
			}//endfor
		}
		
		
		//Update activity feed
		var af_div = document.getElementById("activity_feed");
		var activity_feed = arena.activity_log;
		//console.log(activity_feed);
		var af_len = Object.keys(activity_feed).length;
		var af_diff = (af_len - Object.keys(global_activity_feed).length);
		if (af_diff > 0){
			global_activity_feed = activity_feed;
			
			for (i=af_diff; i>0; i--){
				let header = document.createElement("p");
				header.className = "oog_afheader";
				let header_txt = document.createTextNode(activity_feed[af_len-i][0]);
				header.appendChild(header_txt);
				
				let info = document.createElement("p");
				info.className = "oog_afinfo";
				let info_txt = document.createTextNode(activity_feed[af_len-i][1]);
				info.appendChild(info_txt);
				
				af_div.insertBefore(info, af_div.firstChild);
				af_div.insertBefore(header, af_div.firstChild);
			}
		}
		
		//Remove gladiators that are dead
		var dead_gladiators = arena.dead_gladiators;
		for (dead_glad in dead_gladiators){
			if (global_dead_gladiators.includes(dead_gladiators[dead_glad].id) !== true){
				global_dead_gladiators.push(dead_gladiators[dead_glad].id)
				document.getElementById(dead_gladiators[dead_glad].id).remove();
				document.getElementById("hidden_div_" + dead_gladiators[dead_glad].id).remove();
			}
		}
		
		//Update gladiators
		var gladiators = arena.gladiators;
		for (var gladiator in gladiators){
			let gladiator_obj = arena.gladiators[gladiator];
			let glad_name = gladiator_obj.name;
			let glad_id = gladiator_obj.id;
			
			let health = document.getElementById("health_bar_"+glad_id);
			health.style.width = (Number(gladiator_obj.health)*100)+"%";
			
			let odds = document.getElementById("odds_"+glad_id);
			let status = document.getElementById("status_"+glad_id);
			odds.innerHTML = gladiator_obj.odds;
			status.innerHTML = "Status: " + gladiator_obj.state
			
			let glad_disp = document.getElementById("disp_"+glad_id);
			glad_disp.innerHTML = gladiator_obj.odds +" | HP: "+Math.round(gladiator_obj.health*100);
		}
		
    });//end arena update
	
	
});///End DOC ready






//Build arena upon first entering game
function initArenaGlads(arena_build){
	var table = document.getElementById("arena_grid");
	
	///////////////////
	//Build arena grid
	//////////////////
	var table_html ="";
	for (var tile_row in arena_build.tile_rows) {
		var tr = "<tr>";
		for (var tiles_parser in arena_build.tile_rows[tile_row].tiles){
			//console.log(tile_row, arena_build.tile_rows[tile_row].tiles[tiles_parser])
			var td = "<td class=oog_td_style>";
			td += arena_build.tile_rows[tile_row].tiles[tiles_parser].occupant_initials.join("\n");
			td += "</td>";
			tr += td;
		}
		tr += "</tr>";
		table_html += tr;
	}
	table.innerHTML = table_html;
	//Add terrain extras that may have been placed throughout the game
	for (var tile_row in arena_build.tile_rows) {
		for (var tiles_parser in arena_build.tile_rows[tile_row].tiles){
			var tile = arena_build.tile_rows[tile_row].tiles[tiles_parser]
			var table_td = table.rows[tile_row].cells[tiles_parser]
			if (tile.corpse_present === true){
				table_td.style.backgroundImage = "url('"+cross_img_url+"')";
			}
			if  (tile.hostile === true) { //if hostile
				table_td.style.backgroundColor = "#821111"; 
				table_td.style.outline = null;
			} else if (tile.trap !== false){
				table_td.style.outline = "3px dashed purple";
			}else{
				table_td.style.outline = null;
			}
		}//endfor
	}
	
	
	
	
	///////////////////////
	//Build gladiator view
	//////////////////////
	glad_view = document.getElementById("glad_info")
	glad_ext_view =  document.getElementById("glad_extended")
	var g_v_content = ""
	var g_v_ext = ""
	for (var gladiator in arena_build.gladiators) {
		let gladiator_obj = arena_build.gladiators[gladiator];
		let glad_name = gladiator_obj.name;
		let glad_id = gladiator_obj.id;
		g_v_content += ("<div class='oog_click_div glad_sale' id='" + glad_id
						+ "' onclick=\"showGladInfo('hidden_div_" + glad_id +"');\">");
		g_v_content += "<p>" + glad_name + "</p>";
		g_v_content += "<p id='disp_"+glad_id+"'>" +gladiator_obj.odds +" | HP: "+Math.round(gladiator_obj.health*100)+"</p>";
		g_v_content += "</div>";
		
		//Extended (hidden) gladiator info
		g_v_ext += "<div class='oog_hide oog_center' id='hidden_div_" + glad_id +"'>";
		g_v_ext += "<div class='oog_flex_container'>";//Row 1
		g_v_ext +="<p>" + glad_name +"</p>";
		g_v_ext +="<div class='health_box'><div class='health_bar' id='health_bar_"+glad_id +"'>";
		g_v_ext += "</div></div>";
		//Button to send gift // Current only trap
		if (logged_in === true){
			g_v_ext += ("<button onclick=\"sendGladGift('"+glad_name+"', '" 
							+ glad_id
							+ "', 'gift')\">Send Trap</button>");
		}
		g_v_ext += "</div>";
		
		g_v_ext += "<div class='oog_flex_container'>";//row 2
		g_v_ext += "<p class='odds' id='odds_" + glad_id +"'>"+gladiator_obj.odds+"</p>";
		g_v_ext += "<p id='status_" + glad_id +"'>Status: </p>";
		g_v_ext += "<p id='speed_" + glad_id +"'>Spd: "+ Math.round(gladiator_obj.speed*100) +"</p>";
		g_v_ext += "<p id='strength_" + glad_id +"'>Str: "+ Math.round(gladiator_obj.strength*100) +"</p>";
		g_v_ext += "<p id='aggro_" + glad_id +"'>Agr: "+ Math.round(gladiator_obj.aggro*100) +"</p>";
		g_v_ext += "</div>";
		
		if (logged_in === true){
			g_v_ext += "<div class='oog_flex_container'>";//row 3
			g_v_ext += "<input size='5' type=\"number\" onkeypress=\"return event.charCode >= 48 && event.charCode <= 57\" id=\"bet_" + glad_id + "\">";
			g_v_ext += ("<button id=\"betbut_" + glad_id + "\" onclick=\"sendGladBet('" 
							+ glad_id
							+ "', document.getElementById('bet_" 
							+ glad_id 
							+ "').value, '"+glad_name+"')\">Place Bet</button>");
			
			g_v_ext += "</div>";
		}
						
		g_v_ext += "</div>";//End hidden div
		
	}
	glad_view.innerHTML = g_v_content;
	glad_ext_view.innerHTML = g_v_ext;
	
	//Add event listeners
	if (logged_in === true){
		for (var gladiator in arena_build.gladiators) {
			let gladiator_obj = arena_build.gladiators[gladiator];
			let glad_name = gladiator_obj.name;
			let glad_id = gladiator_obj.id;
			
			let input = document.getElementById("bet_" + glad_id);
			input.addEventListener("keyup", function(event) {
				if (event.keyCode === 13) {//enter key
					document.getElementById("betbut_" + glad_id).click();
				}
			});
		}
	}
	//set dead gladiators
	let dead_gladiators = arena_build.dead_gladiators;
	for (dead_glad in dead_gladiators){
			global_dead_gladiators.push(dead_gladiators[dead_glad].id)
	}
	
	
	
	//////////////////////////////
	//Catch up on activity feed
	////////////////////////////////
	var af_div = document.getElementById("activity_feed");
	var init_activity_feed = arena_grid.activity_log;
	if (init_activity_feed !== undefined) {
		global_activity_feed = init_activity_feed;
		var af_div_fill = "";
		for (var activity in init_activity_feed) {
			af_div_fill = ("<p class=\"oog_afheader\">" + init_activity_feed[activity][0] 
							+ "</p><p class=\"oog_afinfo\">" + init_activity_feed[activity][1] 
							+ "</p>" + af_div_fill);
		}
		af_div.innerHTML = af_div_fill;
	}
	
}//end create func




//Send gladiator bet //VALIDATE THAT USER HAS ENOUGH MONEY
function sendGladBet(glad_id, bet, glad_name){
	let can_buy = enoughMoney(Number(bet));
	document.getElementById('bet_'+glad_id).value = "";
	if (can_buy === true && Number(bet)>0) {
		$.ajax({
			type : "POST",
			url : '/send_glad_bet',
			data: {glad_id: glad_id, bet_amount: bet, game_code: game_code},//This is how to send vars to flask
			success: function(data) { //Update money on screen
				var money_display = document.getElementById("money_display");
				money_display.innerHTML = "Money: " + data;
			}
		});
		swal({
			title: "Bet Placed",
			text: bet+" gold placed on "+glad_name,
			icon: "success",
			timer: 3000
		});
	}
	else{
		console.log("too little cash")
	}
}


//Send gladiator gift
function sendGladGift(glad_name, glad_id, gift){
	var gift_value = 50;
	let can_buy = enoughMoney(gift_value);
	if (can_buy === true){
		swal({
			title:"Send "+glad_name+" a gift?",
			text: "This will cost you " + gift_value,
			icon: "warning",
			buttons: [
				'No',
				'Yes'
			]
		})
		.then((isConfirm) => {
			if(isConfirm) {
				$.ajax({
					type : "POST",
					url : '/send_glad_gift',
					data: {glad_id: glad_id, gift: gift, game_code: game_code, cost: gift_value},//This is how to send vars to flask
					success: function(data) { //Update money on screen
						var money_display = document.getElementById("money_display");
						money_display.innerHTML = "Money: " + data;
					}
				});
				swal({
					title: "Gift Sent!",
					text: "A runner is on their way now",
					icon: "success",
					timer: 2500
				});
			}else{
				console.log("decided against it")
			}
		});
	} else{
		console.log("not enough dosh")
	}
	
}



//Display selected glad div and hide all others
function showGladInfo(div_id){
	let all_hide = document.getElementsByClassName("oog_hide");
	for (i=0; i<all_hide.length; i++){
		all_hide[i].style.display = "none";
	}
	var x = document.getElementById(div_id);
	x.style.display = 'block';
}


//Validate that you have enough cash
function enoughMoney(cost) {
	let user_money = Number(money_display.innerHTML.slice(7))
	if (user_money < cost) {
		console.log("put a swal here saying not enough cash");
		return false;
	}else{
		return true;
	}
}







