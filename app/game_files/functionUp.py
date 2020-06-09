from flask_socketio import SocketIO, emit
from random import random
from time import sleep

def randomNumberGenerator(socketio, param):
    """
    Generate a random number every 1 second and emit to a socketio instance (broadcast)
    Ideally to be run in a separate thread?
    """
    #infinite loop of magical random numbers
    print("Making random numbers")
    while True:
        number = round(random()*10, 3)
        print(number)
        socketio.emit('newnumber', {'number': number}, namespace=param)
        socketio.sleep(3)