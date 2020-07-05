from flask import render_template, flash, redirect, request, url_for
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime
import random as r
import json
from flask_socketio import SocketIO, emit
from threading import Thread
from app import app, db, socketio, moment
from app.models import User, Tournament, Gladiator
from app.email import send_password_reset_email, send_report_issue_email
from app.game_files.nameslist import nameslist
from app.game_files.bioslist import bios
from app.game_files.quoteslist import quotes
from app.game_files.heightlist import heights
from app.forms import LoginForm, RegistrationForm, ResetPasswordForm, SetGameForm,\
						EmptyForm, ResetPasswordRequestForm, ReportIssueForm
						
from app.game_files.game_handler import GameHandler
from datetime import datetime


#Use . to go through directories, so app.game_files.arena etc.

active_games = {}
BONUS_WAIT = 60 #In minutes

@app.before_request
def before_request():
	try:
		global active_games
		del_keys = []
		for game_code in active_games:
			if Tournament.query.filter_by(code=game_code).first() == None:
				del_keys.append(game_code)
		for game_code in del_keys:
			del active_games[game_code]
	except RuntimeError as e:
		print(e)
		print(active_games)
	
	if request.url.startswith('http://'): #Force https
		url = request.url.replace('http://', 'https://', 1)
		code = 301
		return redirect(url, code=code)

	
	
@app.route('/browse_games', methods=['GET','POST'])
def browse_games():
	
	if len(active_games) < 1:
		game = initGame()
		

	form = SetGameForm()
	if form.validate_on_submit():
		
		game = initGame(host=current_user, size=form.size.data, density=form.density.data)
		
		
		return redirect(url_for('game', game_id=game.id))
		
	page = request.args.get('page', 1, type=int)
	games = Tournament.query.order_by(Tournament.id.desc()).paginate(page, app.config['POSTS_PER_PAGE'], False)
	next_url = url_for('browse_games', page=games.next_num) \
											if games.has_next else None
	prev_url = url_for('browse_games', page=games.prev_num) \
											if games.has_prev else None
	return render_template('browse_games.html', games=games.items, form=form,
										next_url=next_url, prev_url=prev_url)




@app.route('/game/<game_id>', methods=['GET', 'POST'])
def game(game_id):
	game = Tournament.query.filter_by(id=game_id).first_or_404()
	global active_games
	if game.code not in active_games:
		return render_template('inactive_game.html')
	game_obj = active_games[game.code]
	json_arena = game_obj.getJSON()

	glads = None
	
	
	barred=0
	if current_user.is_authenticated:
		#reassess battle readiness
		glads_temp = current_user.gladiators.filter(Gladiator.battle_ready < 100)
		for g in glads_temp:
			ready_score = (datetime.utcnow() - g.last_update)
			ready_score = divmod(ready_score.total_seconds(), 60)
			g.battle_ready = int(ready_score[0])
			if g.battle_ready > 100:
				g.battle_ready = 100
			db.session.commit()
				
		glads = current_user.getAvailGlads()
		
		
		if current_user.id in game_obj.barred_users:
			barred=1
		
		print(barred)
		
	return render_template('game.html', game_code=game.code, json_arena=json_arena, barred=barred,
								current_user=current_user, game_bets=game_obj.convertBetsToJSON(),
								init_ua=json.dumps(game_obj.user_activity), glads=glads)


#See what happens if i just try navigating here	
@app.route('/add_gladiator_to_arena', methods=['POST'])
def add_gladiator_to_arena():
	json_glad = json.loads(request.form.get('gladiator'))
	glad = Gladiator.query.filter_by(id=json_glad["id"]).first()
	print(glad)#set gladiator object as "busy" or "in arena"
	glad.available = False
	db.session.commit()
	game_code_key = request.form.get('game_code')
	global active_games
	game = active_games[game_code_key]
	game.addGladiator(glad.name, glad.strength, glad.aggro,
							glad.speed, glad.id, current_user.username, current_user.id)
	return "done"


@app.route('/send_glad_bet', methods=['POST'])
def send_glad_bet():
	glad_id = request.form.get('glad_id')
	bet_amount = request.form.get('bet_amount')
	game_code_key = request.form.get('game_code')
	global active_games
	game = active_games[game_code_key]
	game.sendBet(glad_id, bet_amount, current_user.id)
	return (str(current_user.money))
	

@app.route('/send_glad_gift', methods=['POST'])
def send_glad_gift():
	glad_id = request.form.get('glad_id')
	gift = request.form.get('gift')
	game_code_key = request.form.get('game_code')
	cost = request.form.get('cost')
	global active_games
	game = active_games[game_code_key]
	game.sendGift(glad_id, gift, cost, current_user.id) ##gift var currently unused
	return (str(current_user.money))
	
	
@app.route('/finish_game', methods=['POST'])
def finish_game():
	game_code_key = request.form.get('game_code')
	
	return (str(current_user.money))

	


@app.route('/buy_gladiator', methods=['GET', 'POST'])
def buy_gladiator():
	glad_id = request.form.get('glad_id')
	gladiator = Gladiator.query.filter_by(id=glad_id).first()
	if gladiator != None:
		if gladiator.owner == None:#Check nobody else purchased first
			gladiator.owner = current_user
			current_user.spendMoney(gladiator.getPrice())
			db.session.commit()
			socketio.emit('gladpurchase', {'glad': gladiator.id}, 
							namespace="/marketplace")
		else:
			print("glad unavailable")
			##stuff here to return to user bad

	return str(current_user.money)


	
	
	

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
	page = request.args.get('page', 1, type=int)
	#users = User.query.order_by(User.money_rank.asc()).paginate(page, 20, False)
	users = User.query.filter(User.money_rank!=None).order_by(User.money_rank.asc()).paginate(page, 20, False)
	next_url = url_for('index', page=users.next_num) \
											if users.has_next else None
	prev_url = url_for('index', page=users.prev_num) \
											if users.has_prev else None
											
	return render_template('index.html', users=users.items, title='Home',
										next_url=next_url, prev_url=prev_url)
	
								
@app.route('/marketplace')
@login_required
def marketplace():
	if Gladiator.query.filter_by(owner=None).count() < 20:
		for i in range(20-Gladiator.query.filter_by(owner=None).count()):
			gname = r.choice(nameslist)
			new_glad = Gladiator(name=gname,
							strength=r.randrange(1,99),
							speed=r.randrange(1,99),
							aggro=r.randrange(30,99),
							height= r.choice(heights),
							bio= (r.choice(bios) % {'name': gname}),
							quote= r.choice(quotes),
							available = True,
							owner=None)
			db.session.add(new_glad)
			db.session.commit()
	page = request.args.get('page', 1, type=int)
	glads = Gladiator.query.filter_by(owner=None).paginate(page, app.config['POSTS_PER_PAGE'], False)
	next_url = url_for('marketplace', page=glads.next_num) \
											if glads.has_next else None
	prev_url = url_for('marketplace', page=glads.prev_num) \
											if glads.has_prev else None
	return render_template('marketplace.html', glads=glads.items, 
										next_url=next_url, prev_url=prev_url)



										


@app.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user is None:
			user = User.query.filter_by(email=form.username.data).first()
		if user is None or not user.check_password(form.password.data):
			flash('Invalid username or password')
			return redirect(url_for('login'))
		login_user(user, remember=form.remember_me.data)
		next_page = request.args.get('next')
		if not next_page or url_parse(next_page).netloc != '':
			next_page = url_for('index')
		return redirect(next_page)
	return render_template('login.html', title='Sign In', form=form)
	

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(username=form.username.data, email=form.email.data, money=600)
		user.set_password(form.password.data)
		db.session.add(user)
		db.session.commit()
		flash('Congratulations, you are now a registered user!')
		return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form)
	
	
@app.route('/user/<username>')
def user(username):

	user = User.query.filter_by(username=username).first_or_404()
	
	bonus = False
	if user == current_user:
		#Playing around with timing stuff START

		time_since = (datetime.utcnow() - current_user.last_bonus)
		time_since = divmod(time_since.total_seconds(), 60)

		if time_since[0] >= BONUS_WAIT:
			bonus = True
	
	
	###Gladiator readiness###
	
	if current_user.is_authenticated:
		glads_temp = user.gladiators.filter(Gladiator.battle_ready < 100)
		for g in glads_temp:
			ready_score = (datetime.utcnow() - g.last_update)
			ready_score = divmod(ready_score.total_seconds(), 60)
			print(g.name)
			print(g.battle_ready)
			g.battle_ready = int(ready_score[0])
			if g.battle_ready > 100:
				g.battle_ready = 100
			db.session.commit()
			print(g.battle_ready)
			print(g.last_update)
			print("\n")
	###Gladiator readiness###
	
	
	
	page = request.args.get('page', 1, type=int)
	glads = user.gladiators.order_by(Gladiator.id.desc()).paginate(page, app.config['POSTS_PER_PAGE'], False)
	next_url = url_for('user', username=user.username, page=glads.next_num) \
												if glads.has_next else None
	prev_url = url_for('user', username=user.username, page=glads.prev_num) \
												if glads.has_prev else None
	form = EmptyForm()
	return render_template('user.html', user=user, glads=glads.items, bonus=bonus,
										form=form, next_url=next_url, prev_url=prev_url)



@app.route('/claim_bonus', methods=['GET', 'POST'])
@login_required
def claim_bonus():
	time_since = (datetime.utcnow() - current_user.last_bonus)
	time_since = divmod(time_since.total_seconds(), 60)
	print(time_since[0])
	if time_since[0] >= BONUS_WAIT:
		print(current_user.last_bonus)
		current_user.last_bonus = datetime.utcnow()
		current_user.money = current_user.money + 50
		db.session.commit()
		print(current_user.last_bonus)
	else:
		print("something went wrong")
	return str(current_user.money)



@app.route('/report_issue', methods=['GET', 'POST'])
def report_issue():
	
	form = ReportIssueForm()
	if form.validate_on_submit():
		user = current_user
		if user:
			send_report_issue_email(user, form.description.data)
		flash('Issue reported. Thank you!')
		return redirect(url_for('index'))
		
	return render_template('send_report.html', title="Report Issue", form=form)
	
	
@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = ResetPasswordRequestForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user:
			send_password_reset_email(user)
		flash('Check your email for instructions to reset your password.')
		return redirect(url_for('login'))
	return render_template('reset_password_request.html', title="Reset Password", form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	user = User.verify_reset_password_token(token)
	if not user:
		return redirect(url_for('index'))
	form = ResetPasswordForm()
	if form.validate_on_submit():
		user.set_password(form.password.data)
		db.session.commit()
		flash('Your password has been reset.')
		return redirect(url_for('login'))
	return render_template('reset_password.html', form=form)





def initGame(host=None, size='medium', density='normal'):
	game = Tournament(host=host, size=size, density=density)
	db.session.add(game)
	db.session.commit()
	game.set_code()
	db.session.commit()
	
	global active_games
	game_handler = GameHandler(socketio, game.code, game.id, size, density)
	active_games[game.code] = game_handler
	
	#Start game running
	thread = Thread()
	thread = socketio.start_background_task(game_handler.preGame)
	
	return game












