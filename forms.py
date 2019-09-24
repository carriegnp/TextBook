from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField,SelectField, Form
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from models import User, Post


class RegistrationForm(FlaskForm):
    username = StringField('Username*',validators=[DataRequired(), Length(min=2, max=20)])
    state = StringField('State*', validators=[DataRequired()])
    school = StringField('School*', validators=[DataRequired()])
    email = StringField('Email*',validators=[DataRequired(), Email()])
    password = PasswordField('Password*', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password*',validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('This username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('This email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email*',validators=[DataRequired(), Email()])
    password = PasswordField('Password*', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Log In')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username*',validators=[DataRequired(), Length(min=2, max=20)])
    state = StringField('State*', validators=[DataRequired()])
    school = StringField('School*', validators=[DataRequired()])
    email = StringField('Email*',validators=[DataRequired(), Email()])
    picture = FileField('Upload Profile Picture(.jpg or.png)', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('This username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('This email is taken. Please choose a different one.')


class PostForm(FlaskForm):
    title = StringField('Book_Title*', validators=[DataRequired()])
    book_author = StringField('Book_Author*', validators=[DataRequired()])
    isbn = StringField('Book_ISBN*', validators=[DataRequired()])
    price = StringField('Price*', validators=[DataRequired()])
    course = StringField('Course_Name*', validators=[DataRequired()])
    picture = FileField('Upload Your Selling Book Picture(.jpg/.png/.pdf)', validators=[FileAllowed(['jpg', 'png', 'pdf'])])
    submit = SubmitField('Post')


class RequestResetForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password*', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password*',validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

class SearchForm(FlaskForm):
    
    choices = [('Post', 'All TextBooks')]
    select = SelectField('', choices=choices)
    search = StringField('')

class ContactForm(FlaskForm):
    name = StringField('Name*', validators=[DataRequired()])
    email = StringField('Email*',validators=[DataRequired(), Email()])
    comments =TextAreaField('Comments / Questions*',validators=[DataRequired()] )
    submit = SubmitField('Send Request')



