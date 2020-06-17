from flask import render_template, flash, redirect, request, url_for
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime
import random as r
import json
from flask_socketio import SocketIO, emit
from threading import Thread
from app import app, db, socketio
from app.models import User, Post, Tournament, Gladiator
from app.email import send_password_reset_email
from app.game_files.nameslist import nameslist
from app.forms import LoginForm, RegistrationForm, ResetPasswordForm, \
						EditProfileForm, EmptyForm, PostForm, ResetPasswordRequestForm
						
from app.game_files.functionUp import randomNumberGenerator
from app.game_files.game_handler import GameHandler						
#Use . to go through directories, so app.game_files.arena etc.

active_games = {}##REMEMBER TO REMOVE FROM ACTIVE GAMES ONCE COMPLETE

@app.before_request
def before_request():
	if current_user.is_authenticated:
		current_user.last_seen = datetime.utcnow()
		db.session.commit()




@app.route('/host_game', methods=['GET','POST'])
@login_required
def host_game():
	game = Tournament(host=current_user)
	db.session.add(game)
	db.session.commit()
	game = current_user.hosted_games.order_by(Tournament.id.desc()).first()
	game.set_code()
	db.session.commit()
	
	global active_games
	game_handler = GameHandler(socketio, game.code, game.id)
	active_games[game.code] = game_handler
	
	#Start game running
	thread = Thread()
	thread = socketio.start_background_task(game_handler.preGame)
	return redirect(url_for('game', game_id=game.id))

@app.route('/game/<game_id>', methods=['GET', 'POST'])
def game(game_id):
	game = Tournament.query.filter_by(id=game_id).first_or_404()
	global active_games
	if game.code not in active_games:
		return render_template('404.html')#Maybe put custom error here
	game_obj = active_games[game.code]
	json_arena = game_obj.getJSON()
	return render_template('game.html', game_code=game.code, json_arena=json_arena,
								current_user=current_user, 
								glads=current_user.getAvailGlads())


	
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
							glad.speed, glad.id)
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
	global active_games
	game = active_games[game_code_key]
	game.sendGift(glad_id, gift) ##gift var currently unused
	return "send glad gift"
	
	
@app.route('/finish_game', methods=['POST'])
def finish_game():
	game_code_key = request.form.get('game_code')
	global active_games
	game = active_games[game_code_key]
	game = Tournament.query.filter_by(id=game.game_id).first_or_404()
	del active_games[game_code_key]
	db.session.delete(game)
	db.session.commit()
	win_id = request.form.get('winner')
	print(win_id)
	if (win_id != "None"):
		gladiator = Gladiator.query.filter_by(id=win_id).first()
		gladiator.available = True
		win_owner = gladiator.owner
		win_owner.addMoney(500)
		db.session.commit()
		print(gladiator)
	else:
		print("non player gladiator wins")
	return (str(current_user.money))
	


##Delete a gladiator once dead
@app.route('/remove_glad', methods=['POST'])
def remove_glad():
	glad_id = request.form.get('glad_id')
	Gladiator.query.filter_by(id=glad_id).delete()
	db.session.commit()
	print("deleted")
	return "done"

	

	
@app.route('/buy_gladiator', methods=['GET', 'POST'])
def buy_gladiator():
	glad_id = request.form.get('glad_id')
	gladiator = Gladiator.query.filter_by(id=glad_id).first_or_404()
	gladiator.owner = current_user
	current_user.spendMoney(gladiator.getPrice())
	db.session.commit()
	return str(current_user.money)


	
	
	
	

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
	form = PostForm()
	if form.validate_on_submit():
		post = Post(body=form.post.data, author=current_user)
		db.session.add(post)
		db.session.commit()
		flash('Your post in now live')
		return redirect(url_for('index'))
	page = request.args.get('page', 1, type=int)
	posts = current_user.followed_posts().paginate(
		page, app.config['POSTS_PER_PAGE'], False)
	next_url = url_for('index', page=posts.next_num) if posts.has_next else None
	prev_url = url_for('index', page=posts.prev_num) if posts.has_prev else None
	return render_template('index.html', title='Home', form=form, posts=posts.items,
								next_url=next_url, prev_url=prev_url)
	

@app.route('/explore')
@login_required
def explore():
	page = request.args.get('page', 1, type=int)
	posts = Post.query.order_by(Post.timestamp.desc()).paginate(
		page, app.config['POSTS_PER_PAGE'], False)
	next_url = url_for('explore', page=posts.next_num) if posts.has_next else None
	prev_url = url_for('explore', page=posts.prev_num) if posts.has_prev else None
	return render_template('index.html', title='Explore', posts=posts.items,
								next_url=next_url, prev_url=prev_url)
								
@app.route('/marketplace')
@login_required
def marketplace():
	if Gladiator.query.filter_by(owner=None).count() < 20:
		for i in range(20-Gladiator.query.filter_by(owner=None).count()):
			new_glad = Gladiator(name=r.choice(nameslist),
							strength=r.randrange(99),
							speed=r.randrange(99),
							aggro=r.randrange(30,99),
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
	return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(username=form.username.data, email=form.email.data, money=500)
		user.set_password(form.password.data)
		db.session.add(user)
		db.session.commit()
		flash('Congratulations, you are now a registered user!')
		return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form)
	
	
@app.route('/user/<username>')
@login_required
def user(username):
	user = User.query.filter_by(username=username).first_or_404()
	page = request.args.get('page', 1, type=int)
	glads = user.gladiators.order_by(Gladiator.id.desc()).paginate(page, app.config['POSTS_PER_PAGE'], False)
	next_url = url_for('user', username=user.username, page=glads.next_num) \
												if glads.has_next else None
	prev_url = url_for('user', username=user.username, page=glads.prev_num) \
												if glads.has_prev else None
	form = EmptyForm()
	return render_template('user.html', user=user, glads=glads.items, 
										form=form, next_url=next_url, prev_url=prev_url)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
	form = EditProfileForm(current_user.username)
	if form.validate_on_submit():
		current_user.username = form.username.data
		current_user.about_me = form.about_me.data
		db.session.commit()
		flash('Your changes have been saved.')
		return redirect(url_for('edit_profile'))
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.about_me.data = current_user.about_me
	return render_template('edit_profile.html', title='Edit Profile', form=form)



@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
	form = EmptyForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=username).first()
		if user is None:
			flash('User {} not found'.format(username))
			return redirect(url_for('index'))
		if user == current_user:
			flash('You cannot follow yourself')
			return redirect(url_for('user', username=username))
		current_user.follow(user)
		db.session.commit()
		flash('You are now following {}!'.format(username))
		return redirect(url_for('user', username=username))
	else:
		return redirect(url_for('index'))


@app.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
	form = EmptyForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=username).first()
		if user is None:
			flash('User {} not found'.format(username))
			return redirect(url_for('index'))
		if user == current_user:
			flash('You cannot unfollow yourself')
			return redirect(url_for('user', username=username))
		current_user.unfollow(user)
		db.session.commit()
		flash('You are no longer following {}!'.format(username))
		return redirect(url_for('user', username=username))
	else:
		return redirect(url_for('index'))
		
		
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










		

