$(document).ready(function(){
	//////console.log(game_code)
    //connect to the socket server.
    var socket = io.connect('https://' + document.domain + ':' + location.port + "/"+user_id);
	
	socket.on('betwin', function(msg) {
		toastr.info(msg.winnings+' won on '+msg.glad, 'You Won a Bet', {timeOut: 0, extendedTimeOut: 0})
	});
	
	socket.on('gladwon', function(msg) {
		toastr.success(msg.glad+" won "+msg.winnings, "Gladiator Won", {timeOut: 0, extendedTimeOut: 0})
	});
	
	socket.on('gladdied', function(msg) {
		toastr.error(msg.glad+" has been killed!", "Gladiator Killed", {timeOut: 0, extendedTimeOut: 0})
	});
	
	
});