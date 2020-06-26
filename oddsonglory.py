from app import app, db, socketio
from app.models import User, Gladiator, Tournament
#from app.models import User, Post, Gladiator, Tournament

if __name__ == '__main__':
	socketio.run(app)

@app.shell_context_processor
def make_shell_context():
	return {'db': db, 'User': User, 'Post': Post, 'Gladiator': Gladiator, 'Tournament': Tournament}
