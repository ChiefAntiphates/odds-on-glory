
$(document).ready(function(){
	console.log("bing")
	console.log(game_code)
    //connect to the socket server.
    var socket = io.connect('http://' + document.domain + ':' + location.port + game_code);
    
	
	var table = document.getElementById("arena_grid");
	var arena_build = json_arena;
	
	for (var tile_row in arena_build.tile_rows) {
		console.log(tile_row, arena_build.tile_rows[tile_row])
		var tr = "<tr>";
		
		for (var tiles_parser in arena_build.tile_rows[tile_row].tiles){
			console.log(tile_row, arena_build.tile_rows[tile_row].tiles[tiles_parser])
			var td = "<td class=outline_temp>";
			td += arena_build.tile_rows[tile_row].tiles[tiles_parser].x_co;
			td += arena_build.tile_rows[tile_row].tiles[tiles_parser].y_co;
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
	});
	
	

    //receive details from server
    socket.on('arenaupdate', function(msg) {
		var arena = JSON.parse(msg.json_obj);
		console.log(arena)
        var table = document.getElementById("arena_grid");
        //for (var i = 0; i < numbers_received.length; i++){
         //   numbers_string = numbers_string + '<p>' + numbers_received[i].toString() + '</p>';
       //}
        $('#log').html("<p>"+arena+"</p>");
    });

});