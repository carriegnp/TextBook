from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:123456@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = '\x0c\xb9\x1b}\x9a\x1al\xf9\x04\x95\xe8.\xa2G\xedF\xc4m\xa1\x87\xc7\x88\x9c\xce'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), unique=True)
    body = db.Column(db.String(120))

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/')
def index():
    return redirect ('/blog')


@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    if request.method == 'POST':
        new_blog_title = request.form['title']
        new_blog_body = request.form['body']

        if new_blog_title == '':
            flash('Please fill in the title', 'error')
            return render_template ('newpost.html', description='Add a blog entry')
        elif new_blog_body=='':
            flash('Please fill in the body', 'error')
            return render_template ('newpost.html', description='Add a blog entry')
        else:
            new_blog=Blog(new_blog_title,new_blog_body)
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/blog?id={}'.format(new_blog.id))
       
    return render_template ('newpost.html', description='Add a blog entry')

@app.route('/blog', methods=['POST','GET'])
def blog():
    if request.method=='GET' and request.args.get('id'):
        blog_id=request.args.get('id')
        blog=Blog.query.get(blog_id)
        return render_template('individual.html', blog=blog)
    if request.method=='POST' or request.method=='GET': 
        blogs=Blog.query.all()
        return render_template('blog.html', description='Build a blog', blogs=blogs)


if __name__ == '__main__':
    app.run()

    