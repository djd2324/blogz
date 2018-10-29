from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:Smokey0!@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key='lskjf38290'
db = SQLAlchemy(app)

class Blog(db.Model):    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100))
    body = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner
        
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(30))
    posting = db.relationship('Blog', backref='owner')

    

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'register', 'index', 'singleuser']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

#user index page

@app.route('/index', methods=['POST', 'GET'])
def index():
    authors = User.query.all()
    if request.method == 'GET':

        return render_template('index.html', authors=authors)

        


#home

@app.route('/', methods=['POST', 'GET'])
def home():

    title_error = ""
    body_error = ""
    owner = User.query.filter_by(username=session['username']).first()


    blogs = Blog.query.all()
    
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        owner = User.query.filter_by(username=session['username']).first()
        
        if not title:
            title_error="required field"

        if not body:
            body_error="required field"

        if not title or not body:
            return render_template('home.html', blogs=blogs, title_error=title_error, body_error=body_error, owner=owner)

        new_blog = Blog(title, body, owner)
        db.session.add(new_blog)
        db.session.commit()
        new_blog_id = new_blog.id
        return redirect('/blog?id={0}'.format(new_blog.id))

    return render_template('home.html', blogs=blogs)


#single user

@app.route('/singleuser', methods=['POST', 'GET'])
def singleuser():
    allblogs = Blog.query.all()

    
    user_id=str(request.args.get('user'))
    users = Blog.query.filter_by(owner_id=user_id).all()
    return render_template('singleuser.html', users=users)
    

#blog

@app.route('/blog', methods=['POST', 'GET'])
def blog():
    
    blog_id=request.args.get('id')
    blog_id_int=int(blog_id)
    blog = Blog.query.filter_by(id=blog_id_int).first()
    if blog:
        return render_template('blog.html', blog=blog)
    
    else:
        return 'Not Found'


#login


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username'] 
        password = request.form['password'] 
        user = User.query.filter_by(username=username).first()
        
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')


 
 
 #register

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        passworderror = ''
            
       

 # validate user's data

        existing_user = User.query.filter_by(username=username).first()
        
        if len(password)==0:
            passworderror = 'password required'
            
            return render_template('register.html', username=username, passworderror=passworderror)
        
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/')
        else:
            
            return "<h1>User Exists</h1>"

    return render_template('register.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')
 



if __name__ == '__main__':
    app.run()