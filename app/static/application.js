
$(document).ready(function(){
	console.log("bing")
	console.log(game_code)
    //connect to the socket server.
    var socket = io.connect('http://' + document.domain + ':' + location.port + game_code);
    
	
	var table = document.getElementById("arena_grid");
	var arena_build = json_arena;
	
	for (var tile_row in arena_build.tile_rows) {
		//console.log(tile_row, arena_build.tile_rows[tile_row])
		var tr = "<tr>";
		
		for (var tiles_parser in arena_build.tile_rows[tile_row].tiles){
			//console.log(tile_row, arena_build.tile_rows[tile_row].tiles[tiles_parser])
			var td = "<td class=oog_outline_temp>";
			td += arena_build.tile_rows[tile_row].tiles[tiles_parser].occupant_initials;
			td += "</td>";
			tr += td;
		}
		
		tr += "</tr>";
		table.innerHTML += tr;
	}
	
	//for tiles_row in arena_build:
	//	console.log(tiles_row);


	var button = document.createElement("button");
	button.innerHTML = "Do Something";
	document.getElementById("testbut").appendChild(button)
	
	button.addEventListener("click", function() {
		$.ajax({
			type : "POST",
			url : start_url
		});
		elem = document.getElementById("testbut")
		elem.parentNode.removeChild(elem);
	});
	
	

    //receive details from server
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
		
		//Update gladiators
		glad_view = document.getElementById("glad_info")
		var g_v_content = ""
		for (var gladiator in arena.gladiators) {
			g_v_content += "<p>" + arena.gladiators[gladiator].name + "</p>";
		}
		glad_view.innerHTML = g_v_content;
		
        //for (var i = 0; i < numbers_received.length; i++){
         //   numbers_string = numbers_string + '<p>' + numbers_received[i].toString() + '</p>';
       //}
        $('#log').html("<p>"+arena+"</p>");
    });

});