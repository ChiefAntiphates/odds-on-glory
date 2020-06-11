//var global_glad_list = []

$(document).ready(function(){
	console.log(game_code)
    //connect to the socket server.
    var socket = io.connect('http://' + document.domain + ':' + location.port + game_code);
    
	//Upon connecting build arena incase missed the update
	initArenaGlads(json_arena)
	
	
	
	

	socket.on('gladiatoradding', function(msg) {
		var gladiatoradding_arena = JSON.parse(msg.json_obj);
		glad_view = document.getElementById("glad_info")
		var g_v_content = ""
		for (var gladiator in gladiatoradding_arena.gladiators) {
			var glad_name = gladiatoradding_arena.gladiators[gladiator].name;
		
			g_v_content += "<p>" + glad_name + "</p>";
			g_v_content += "<br><br>";
		}
		glad_view.innerHTML = g_v_content;
	});
	
	
	socket.on('arenainitial', function(msg) {
		var arena_initial_in = JSON.parse(msg.json_obj);
		initArenaGlads(arena_initial_in)
	});
	

    //Upon Socket arena update event
    socket.on('arenaupdate', function(msg) {
		var arena = JSON.parse(msg.json_obj);
		console.log(arena);
		
		//Update tiles
        var table = document.getElementById("arena_grid");
		for (var tile_row in arena.tile_rows) {
			for (var tiles_parser in arena.tile_rows[tile_row].tiles){
				var occ = arena.tile_rows[tile_row].tiles[tiles_parser].occupant_initials;
				table.rows[tile_row].cells[tiles_parser].innerHTML = occ;
			}
		}
		
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
	var table_html =""
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
		g_v_content += "</div>";
		
		//Pass gladiator obj into function then display there instead
		g_v_content += "<div class='oog_hide' id='hidden_div_" + glad_name +"' style:>";
		g_v_content += "<input type=\"text\" id=\"bet_" + glad_name + "\">";
		g_v_content += ("<button onclick=\"sendGladBet('" 
						+ glad_name
						+ "', document.getElementById('bet_" 
						+ glad_name 
						+ "').value)\">Click</button>");
		g_v_content += "</div>"
		g_v_content += "<br><br>";
	}
	glad_view.innerHTML = g_v_content;
	
}//end func


function showGladInfo(div_id){
	var x = document.getElementById(div_id);
	x.style.display = 'block';
}



//Start arena games button
	/*var button = document.createElement("button");
	button.innerHTML = "Do Something";
	document.getElementById("start_games_but").appendChild(button)
	button.addEventListener("click", function() {
		$.ajax({
			type : "POST",
			url : start_url,
			data: {temp_data: "halloball"}//This is how to send vars to flask
		});
		elem = document.getElementById("start_games_but")
		elem.parentNode.removeChild(elem);
	});*/