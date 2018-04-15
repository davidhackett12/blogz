from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:launchcode@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key= True)
    title = db.Column(db.String(120))
    content = db.Column(db.String(2000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    pub_date = db.Column(db.DATETIME)

    def __init__(self,title,content, owner, pub_date=None):
        self.title = title
        self.content = content
        self.owner = owner 
        if pub_date is None:
            pub_date = datetime.utcnow()
        self.pub_date = pub_date

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique= True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref= 'owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

    
@app.route('/blog')
def blog():
    blog_id = request.args.get("id")
    if blog_id:
        blog = Blog.query.filter_by(id=blog_id).first()
        return render_template('oldpost.html', title = blog.title, content = blog.content)
    else:
        posts = Blog.query.order_by("pub_date desc").all()
        return render_template('blog.html', posts = posts)


   
@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    owner = User.filter_by(username=session['username']).first()
    if request.method == 'POST':
        blog_title = request.form['title']
        blog_content = request.form['content']

        if blog_title == "":
            title_error = "You did not include a title for your blog"
        else:
            title_error = ""

        if blog_content == "":
            content_error = "You did not include any content"
        else:
            content_error = ""
        
        if content_error or title_error:
            return render_template('newpost.html', title= blog_title, content= blog_content, title_error = title_error, content_error = content_error)
        else:
            new_blog = Blog(blog_title, blog_content, owner)
            db.session.add(new_blog)
            db.session.commit()
            id_str = str(new_blog.id)

            return redirect('/blog?id='+id_str)
    
    return render_template('newpost.html', title = "", content= "", title_error = "", content_error = "")

@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            return redirect('/newpost')
        else:
            flash('Username and password combo is incorrect')

if __name__ == '__main__':
    app.run() 







