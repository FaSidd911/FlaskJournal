from flask import Flask,render_template,request,redirect
from flask_login import login_required, current_user, login_user, logout_user
from models import UserModel,db,login,entries
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String,Table
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'xyz'
 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
 
 
db.init_app(app)
login.init_app(app)
login.login_view = 'login'
 
@app.before_first_request
def create_all():
    db.create_all()


     
@app.route('/blogs' , methods = ['POST', 'GET'])
@login_required
def blog():
    topics = entries.query.filter_by(email = current_user.email)
    if request.method == 'POST':
        header = request.form['title']
        body = request.form['text']
        entry = entries(email=current_user.email, body=body,header = header)
        db.session.add(entry)
        db.session.commit()
        return redirect('/blogs')

    return render_template('blog.html', result = topics)

@app.route('/add' , methods = ['POST', 'GET'])
@login_required
def add():
    if request.method == 'POST':
        header = request.form['title']
        body = request.form['text']
        entry = entries(email=current_user.email, body=body,header = header,date_posted=datetime.now())
        db.session.add(entry)
        db.session.commit()
        return redirect('/add')

    return render_template('add.html')

@app.route("/view")
@login_required
def post():
    p = entries.query.all()
    p = sorted(p, key=lambda x:x.date_posted, reverse=True)
    return render_template('posts.html', post= p, title="Entries")

@app.route("/del/<int:pid>")
@login_required
def delete(pid):
    p = entries.query.filter_by(pid = pid).delete()
    db.session.commit()
    return redirect("/view")

@app.route("/edit/<int:pid>", methods = ['POST', 'GET'])
@login_required
def edit(pid):
    post = entries.query.get(pid)
    if request.method == 'POST':
        post.header = request.form['title']
        post.body = request.form['text']
        post.date_posted = datetime.now()
        db.session.commit()
        return redirect("/view")
    return render_template('edit.html', p=post)


@app.route('/login', methods = ['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect('/view')
     
    if request.method == 'POST':
        email = request.form['email']
        user = UserModel.query.filter_by(email = email).first()
        if user is not None and user.check_password(request.form['password']):
            login_user(user)
            return redirect('/view')
     
    return render_template('login.html')
 
@app.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect('/view')
     
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
 
        if UserModel.query.filter_by(email=email).first():
            return ('Email already Present')
             
        user = UserModel(email=email, username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return redirect('/login')
    return render_template('register.html')
 
 
@app.route('/logout')
def logout():
    logout_user()
    return redirect('/blogs')
app.run()
