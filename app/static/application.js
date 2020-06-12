//var global_glad_list = [];
var global_activity_feed = [];

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
		
		
		
		//Update tiles
        var table = document.getElementById("arena_grid");
		for (var tile_row in arena.tile_rows) {
			for (var tiles_parser in arena.tile_rows[tile_row].tiles){
				var occ = arena.tile_rows[tile_row].tiles[tiles_parser].occupant_initials;
				table.rows[tile_row].cells[tiles_parser].innerHTML = occ;
			}
		}
		
		//Update activity feed
		//Maybe just add new instead of full update each time
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
		
		/*
		var af_div_fill = "";
		for (var activity in activity_feed) {
			af_div_fill = ("<p class=\"oog_afheader\">" + activity_feed[activity][0] 
							+ "</p><p class=\"oog_afinfo\">" + activity_feed[activity][1] 
							+ "</p>" + af_div_fill);
		}
		af_div.innerHTML = af_div_fill;
		*/
		
		
		
		
		//Loop through dead gladiators and delete divs with their id
		//Update gladiators
		//var local_glad_list = arena.gladiators;
		//if ((Object.keys(local_glad_list).length == Object.keys(global_glad_list).length) == false) {
		//	global_glad_list = local_glad_list;
		
		//}
    });
	
});


//Test function
function sendGladBet(name, bet){
	console.log("we hereeee")
	document.getElementById('bet_'+name).value = "";
	$.ajax({
		type : "POST",
		url : '/test_send_request',
		data: {glad_name: name, bet_amount: bet}//This is how to send vars to flask
	});
}



function initArenaGlads(arena_build){
	var table = document.getElementById("arena_grid");
	
	//Build arena grid
	var table_html ="";
	for (var tile_row in arena_build.tile_rows) {
		var tr = "<tr>";
		for (var tiles_parser in arena_build.tile_rows[tile_row].tiles){
			//console.log(tile_row, arena_build.tile_rows[tile_row].tiles[tiles_parser])
			var td = "<td class=oog_outline_temp>";
			td += arena_build.tile_rows[tile_row].tiles[tiles_parser].occupant_initials;
			td += "</td>";
			tr += td;
		}
		tr += "</tr>";
		table_html += tr;
	}
	table.innerHTML = table_html;
	
	//Build gladiator view
	glad_view = document.getElementById("glad_info")
	var g_v_content = ""
	for (var gladiator in arena_build.gladiators) {
		var glad_name = arena_build.gladiators[gladiator].name;
		g_v_content += ("<div class='oog_click_div' id='div_" + glad_name
						+ "' onclick=\"showGladInfo('hidden_div_" + glad_name +"');\">");
		g_v_content += "<p>" + glad_name + "</p>";
		
		
		//Pass gladiator obj into function then display there instead
		g_v_content += "<div class='oog_hide' id='hidden_div_" + glad_name +"'>";
		g_v_content += "<input type=\"text\" id=\"bet_" + glad_name + "\">";
		g_v_content += ("<button onclick=\"sendGladBet('" 
						+ glad_name
						+ "', document.getElementById('bet_" 
						+ glad_name 
						+ "').value)\">Click</button>");
		g_v_content += "</div>";
		g_v_content += "</div>";
	}
	glad_view.innerHTML = g_v_content;
	
	
	
	//Catch up on activity feed
	var af_div = document.getElementById("activity_feed");
	var init_activity_feed = arena_grid.activity_log;
	console.log(init_activity_feed);
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
	
}//end func


function showGladInfo(div_id){
	var x = document.getElementById(div_id);
	if (x.style.display === 'block') {
		x.style.display = 'none';
	} else {
		x.style.display = 'block';
	}
}