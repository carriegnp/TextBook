from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from hashutils import make_pw_hash, check_pw_hash
from datetime import datetime


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:123456@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = '\x0c\xb9\x1b}\x9a\x1al\xf9\x04\x95\xe8.\xa2G\xedF\xc4m\xa1\x87\xc7\x88\x9c\xce'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))
    pub_date = db.Column(db.DateTime, nullable=False,default=datetime.utcnow)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    pw_hash = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.pw_hash = make_pw_hash(password)

@app.before_request
def require_login():
    allowed_routes = ['login','blog','signup', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_pw_hash(password, user.pw_hash):
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost')
        elif user and not check_pw_hash(password, user.pw_hash):
            flash('user password is incorrect', 'error')
        elif not user:
            flash('user does not exist', 'error')     
    return render_template('login.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        verify = request.form.get('verify')

        if username=='' or password=='' or verify == '':
            flash('one or more fields are empty', 'error')
           
            
        elif verify != password:
            flash('password does not match', 'error')
           

        elif len(username)<3 or len(password)<3:
            flash('username or password length must be longer than 3', 'error')
           
        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            flash('successfully signed up!')
            return redirect('/newpost')
        else:
            flash('username is already taken', 'error')
            
    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')


@app.route('/', methods=['POST','GET'])
def index():
        users=User.query.all()
        return render_template('index.html', users=users)


@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    owner = User.query.filter_by(username=session['username']).first()
    if request.method == 'POST':
        new_blog_title = request.form.get('title')
        new_blog_body = request.form.get('body')

        if new_blog_title == '':
            flash('Please fill in the title', 'error')
            
        elif new_blog_body=='':
            flash('Please fill in the body', 'error')
            
        else:
            new_blog=Blog(new_blog_title,new_blog_body, owner)
            db.session.add(new_blog)
            db.session.commit()
            return render_template('individual.html', blog=new_blog)
       
    return render_template ('newpost.html')

@app.route('/blog', methods=['POST','GET'])
def blog():
    page_num=request.args.get('page',1, type=int)
    blogs = Blog.query.order_by(Blog.pub_date.desc()).paginate(page=page_num, per_page=3)
    users = User.query.all()
    blog_id = request.args.get("id")
    user_username = request.args.get("user")
    
    if blog_id:
        blog = Blog.query.filter_by(id=blog_id).first()
        return render_template('individual.html', blog=blog)
        
    if user_username:
        page=request.args.get('page',1,type=int)
        user = User.query.filter_by(username=user_username).first()
        user_blogs = Blog.query.filter_by(owner_id=user.id).order_by(Blog.pub_date.desc()).paginate(page=page, per_page=4)
        return render_template('singleUser.html', blogs=user_blogs, user=user)

    else:
        return render_template('blog.html', blogs=blogs)


if __name__ == '__main__':
    app.run()

    