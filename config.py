import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'artichokey-nono'
	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
		'sqlite:///' +  os.path.join(basedir, 'app.db')
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	
	MAIL_SERVER = 'smtp.googlemail.com'
	MAIL_PORT = '587'
	MAIL_USE_TLS = '1'
	MAIL_USERNAME = 'noreply.oddsonglory@gmail.com'
	MAIL_PASSWORD = 'D5WAtTiC39e28az'
	ADMINS = ['noreply.oddsonglory@gmail.com', 'oddsonglory@gmail.com']
	
	POSTS_PER_PAGE = 11
	
	LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
	#LANGUAGES = ['en', 'es']