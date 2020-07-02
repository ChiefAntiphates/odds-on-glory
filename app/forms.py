from flask_wtf import FlaskForm
from sqlalchemy import func
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from app.models import User


class LoginForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember_me = BooleanField('Remember Me')
	submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	password2 = PasswordField(
		'Repeat Password', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Register')

	def validate_username(self, username):
		user = User.query.filter(func.lower(User.username)==username.data.lower()).first()
		if user is not None:
			raise ValidationError('Username taken. Please choose a different username.')
		if " " in username.data:
			raise ValidationError('Usernames can be only one word.')
	
	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user is not None:
			raise ValidationError('Email in use. Please use a different email address.')




class EmptyForm(FlaskForm):
	submit = SubmitField('Submit')
	

#This can be replaced as the activity log
class PostForm(FlaskForm):
	post = TextAreaField('Say something', validators=[
		DataRequired(), Length(min=1, max=140)])
	submit = SubmitField('Submit')
	
	
class ResetPasswordRequestForm(FlaskForm):
	email = StringField('Email', validators=[DataRequired(), Email()])
	submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
	password = PasswordField('Password', validators=[DataRequired()])
	password2 = PasswordField(
		'Repeat Password', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Reset Password')


class SetGameForm(FlaskForm):
	size = SelectField('Size:', choices=[('small', 'Small'), ('medium', 'Medium'), ('large', 'Large')])
	density = SelectField('Density:', choices=[('sparse', 'Sparse'), ('normal', 'Normal'), ('packed', 'Packed')])
	submit = SubmitField('Host Game')









	

		
		