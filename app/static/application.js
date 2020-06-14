//var global_glad_list = [];
var global_activity_feed = [];
var global_dead_gladiators = [];

$(document).ready(function(){
	console.log(game_code)
    //connect to the socket server.
    var socket = io.connect('http://' + document.domain + ':' + location.port + game_code);
    
	//Upon connecting build arena incase missed the update
	initArenaGlads(json_arena)
	
	
	
	
	//Add gladiator button - removed at start of betting phase
	if (json_arena.active == false){
		var button = document.createElement("button");
		button.innerHTML = "Add Gladiator";
		document.getElementById("add_glad_but").appendChild(button)
		button.addEventListener("click", function() {
			$.ajax({
				type : "POST",
				url : '/add_gladiator_to_arena',
				data: {gladiator: "printing glad", game_code: game_code}//This is how to send vars to flask
			});
		});
	}
	
	
	//SOCKET RESPONSES
	
	//Socket response to a new gladiator added
	socket.on('gladiatoradding', function(msg) {
		var gladiatoradding_arena = JSON.parse(msg.json_obj);
		glad_view = document.getElementById("glad_info")
		var g_v_content = ""
		for (var gladiator in gladiatoradding_arena.gladiators) {
			var glad_name = gladiatoradding_arena.gladiators[gladiator].name;
		
			g_v_content += "<p>" + glad_name + "</p>";
			g_v_content += "<br>";
		}
		glad_view.innerHTML = g_v_content;
	});
	
	
	//Socket response to initialise the betting phase
	socket.on('arenainitial', function(msg) {
		elem = document.getElementById("add_glad_but")
		elem.parentNode.removeChild(elem);//Remove add gladiator button
		var arena_initial_in = JSON.parse(msg.json_obj);
		initArenaGlads(arena_initial_in)
	});
	

    //Upon Socket arena update event
    socket.on('arenaupdate', function(msg) {
		var arena = JSON.parse(msg.json_obj);
		//console.log(arena);
		
		
		//Update tiles//NOTE: Convert to canvas at some point
        var table = document.getElementById("arena_grid");
		for (var tile_row in arena.tile_rows) {
			for (var tiles_parser in arena.tile_rows[tile_row].tiles){
				var tile = arena.tile_rows[tile_row].tiles[tiles_parser];
				var table_td = table.rows[tile_row].cells[tiles_parser];
				//table_td.innerHTML = tile.occupant_initials.join("\n");
				let canvas = table_td.firstChild;
				let ctx = canvas.getContext("2d")
				ctx.clearRect(0,0,50,50);
				ctx.font = "14px Arial";
				ctx.fillText(tile.occupant_initials.join(""), 10.5, 20.5);
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
		//Loop through dead gladiators and delete divs with their id
		//Update gladiators
		//var local_glad_list = arena.gladiators;
		//if ((Object.keys(local_glad_list).length == Object.keys(global_glad_list).length) == false) {
		//	global_glad_list = local_glad_list;
		
		
    });
	
});






//Build arena upon first entering game
function initArenaGlads(arena_build){
	var table = document.getElementById("arena_grid");
	
	//Build arena grid
	var table_html ="";
	for (var tile_row in arena_build.tile_rows) {
		var tr = "<tr>";
		for (var tiles_parser in arena_build.tile_rows[tile_row].tiles){
			//console.log(tile_row, arena_build.tile_rows[tile_row].tiles[tiles_parser])
			var td = "<td class=oog_td_style>";
			//td += arena_build.tile_rows[tile_row].tiles[tiles_parser].occupant_initials.join("\n");
			td += "<canvas width=\"50\" height=\"50\"></canvas>";
			td += "</td>";
			tr += td;
		}
		tr += "</tr>";
		table_html += tr;
	}
	table.innerHTML = table_html;

	for (var tile_row in arena_build.tile_rows) {
		for (var tiles_parser in arena_build.tile_rows[tile_row].tiles){
			var tile = arena_build.tile_rows[tile_row].tiles[tiles_parser];
			var table_td = table.rows[tile_row].cells[tiles_parser];
			let canvas = table_td.firstChild;
			let ctx = canvas.getContext("2d")
			ctx.font = "14px Arial";
			ctx.fillText(tile.occupant_initials.join(""), 10.5, 20.5);
		}
	}
	
	
	//Build gladiator view
	glad_view = document.getElementById("glad_info")
	glad_ext_view =  document.getElementById("glad_extended")
	var g_v_content = ""
	var g_v_ext = ""
	for (var gladiator in arena_build.gladiators) {
		var gladiator_obj = arena_build.gladiators[gladiator];
		var glad_name = gladiator_obj.name;
		var glad_id = gladiator_obj.id;
		g_v_content += ("<div class='oog_click_div' id='" + glad_id
						+ "' onclick=\"showGladInfo('hidden_div_" + glad_id +"');\">");
		g_v_content += "<p>" + glad_name + "</p>";
		g_v_content += "</div>";
		
		
		g_v_ext += "<div class='oog_hide oog_center' id='hidden_div_" + glad_id +"'>";
		g_v_ext +="<p>" + glad_name +"</p>";
		
		//Button to send bet //Replace these with glad IDs
		g_v_ext += "<input type=\"text\" id=\"bet_" + glad_id + "\">";
		g_v_ext += ("<button onclick=\"sendGladBet('" 
						+ glad_id
						+ "', document.getElementById('bet_" 
						+ glad_id 
						+ "').value)\">Click</button>");
						
		//Button to send gift
		g_v_ext += ("<button onclick=\"sendGladGift('" 
						+ glad_id
						+ "', 'gift')\">Send Trap</button>");
		
		g_v_ext += "</div>";
		
	}
	glad_view.innerHTML = g_v_content;
	glad_ext_view.innerHTML = g_v_ext;
	
	
	
	//Catch up on activity feed
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




//Send gladiator bet
function sendGladBet(glad_id, bet){
	console.log("we hereeee")
	document.getElementById('bet_'+glad_id).value = "";
	$.ajax({
		type : "POST",
		url : '/test_send_request',
		data: {glad_id: glad_id, bet_amount: bet}//This is how to send vars to flask
	});
}


//Send gladiator gift
function sendGladGift(glad_id, gift){
	$.ajax({
		type : "POST",
		url : '/send_glad_gift',
		data: {glad_id: glad_id, gift: gift, game_code: game_code}//This is how to send vars to flask
	});
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



