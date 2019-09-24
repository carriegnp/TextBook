import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from app import app, db, bcrypt, mail
from forms import (RegistrationForm, LoginForm, ContactForm, UpdateAccountForm, PostForm, SearchForm, RequestResetForm, ResetPasswordForm)
from models import User, Post, Guest
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
app.secret_key = '\x0c\xb9\x1b}\x9a\x1al\xf9\x04\x95\xe8.\xa2G\xedF\xc4m\xa1\x87\xc7\x88\x9c\xce'


    
@app.route('/', methods=['GET', 'POST'])
def index():
    search = SearchForm(request.form)
    if request.method == 'POST':
        return search_results(search)
 
    return render_template('index.html', form=search)
 
 
@app.route('/results')
def search_results(search):
    results = []
 
    if search.data['search'] == '':
        qry = db.session.query(Post)
        results =qry.all()
 
    if not results:
        flash('No results found!')
        return redirect('/')
    else:
        # display results
        return render_template('results.html', results=results)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        guest = Guest(name=form.name.data, email=form.email.data,comments=form.comments.data)
        db.session.add(guest)
        db.session.commit()
        flash('We have received your message!')
        
    return render_template('contacts.html', title='Contact',form=form)
    

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return render_template('logout.html', title = "Log Out")

@app.route("/buyBook")
def buyBook():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('buyBook.html', posts=posts, page = page, title="Buy Book")


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash('You are a current user already')
        return redirect('/account')

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(state=form.state.data, school=form.school.data, username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to sell your book!')
        return redirect('/sellBook')
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('You are a current user already')
        return redirect('/account')
        
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect("/sellBook")
        else:
            flash('Login is unsuccessful. Please make sure email and password are correct.')
    return render_template('login.html', title='Login', form=form)

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.state = form.state.data
        current_user.school = form.school.data
        current_user.picture= save_picture(form.picture.data)
        db.session.commit()
        flash('Your account has been updated!')
        return redirect('/buyBook')
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.state.data = current_user.state
        form.school.data = current_user.school
    return render_template('account.html', title='Account',form=form)

@app.route("/sellBook", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data,book_author=form.book_author.data, isbn=form.isbn.data, price=form.price.data,course=form.course.data, picture= save_picture(form.picture.data), author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!')
        return redirect('/user_posts')
    return render_template('sellBook.html', title='Sell Book',form=form)


@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.book_author = form.book_author.data
        post.isbn = form.isbn.data
        post.price = form.price.data
        post.course = form.course.data
        post.picture=save_picture(form.picture.data)
        db.session.commit()
        flash('Your post has been updated!')
        return redirect(url_for('user_posts', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.book_author.data = post.book_author
        form.isbn.data=post.isbn
        form.price.data=post.price
        form.course.data=post.course
    return render_template('sellBook.html', title='Update Post',form=form)


@app.route("/post/<int:post_id>/delete", methods=['POST'])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!')
    return redirect(url_for('user_posts'))


@app.route("/user_posts")
@login_required
def user_posts():
    if current_user.is_authenticated:
        page = request.args.get('page', 1, type=int)
        posts = Post.query.filter_by(author=current_user).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
        return render_template('user_posts.html', posts=posts, user=current_user, title='All Posts Under You')


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('account'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('account'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)

if __name__ == '__main__':
    app.run(debug=True)