from app import app, db#,socketio
from app.models import User, Post

if __name__ == '__main__':
	app.run()

@app.shell_context_processor
def make_shell_context():
	return {'db': db, 'User': User, 'Post': Post}
	
##Use socketio with an array of threads, using dynamic namespaces and URLs (maybe with db)
##https://www.shanelynn.ie/asynchronous-updates-to-a-webpage-with-flask-and-socket-io/