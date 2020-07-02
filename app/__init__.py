from flask import Flask, request
from config import Config
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_moment import Moment
from flask_socketio import SocketIO, emit
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
import atexit
from sqlalchemy.orm import aliased
from sqlalchemy import func	
from apscheduler.schedulers.background import BackgroundScheduler


application = app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
mail = Mail(app)
moment = Moment(app)
socketio = SocketIO(app, async_mode=None, logger=False, engineio_logger=False)



##Updating money rankings
from app.models import User, Tournament, Gladiator
def update_money_rankings():
	u1 = aliased(User)
	subq = db.session.query(func.count(u1.id)).filter(u1.money > User.money).as_scalar()
	db.session.query(User).update({"money_rank": subq + 1}, synchronize_session=False)
	db.session.commit()
	#print("ranks updated")

scheduler = BackgroundScheduler()
scheduler.add_job(func=update_money_rankings, trigger="interval", seconds=60)
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())



if not app.debug:
	if app.config['MAIL_SERVER']:
		auth = None
		if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
			auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
		secure = None
		if app.config['MAIL_USE_TLS']:
			secure = ()
		mail_handler = SMTPHandler(
			mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
			fromaddr='no-reply@' + app.config['MAIL_SERVER'],
			toaddrs=app.config['ADMINS'], subject='Bug or Failure - OddsOnGlory',
			credentials=auth, secure=secure)
		mail_handler.setLevel(logging.ERROR)
		app.logger.addHandler(mail_handler)
	
	if app.config['LOG_TO_STDOUT']:
		stream_handler = logging.StreamHandler()
		stream_handler.setLevel(logging.INFO)
		app.logger.addHandler(stream_handler)
	else:
		if not os.path.exists('logs'):
			os.mkdir('logs')
		file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240, backupCount=10)
		file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
		file_handler.setLevel(logging.INFO)
		app.logger.addHandler(file_handler)
	app.logger.setLevel(logging.INFO)
	app.logger.info('OddsOnGlory Game')
	
	



from app import routes, models, errors

