from flask import Flask
from flask import Flask, flash, redirect, render_template, request, session, abort
import os
from sqlalchemy.orm import sessionmaker
from tabledef import *
import uuid
from flask_login import LoginManager

engine = create_engine('sqlite:///tutorial.db', echo=True)

app = Flask(__name__)
app.secret_key = str(uuid.uuid4())

user = ""

@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('index.html')
    else:
        return render_template('index.html', user=user)

@app.route('/logon')
def logon():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return "Already logged in!"

@app.route('/login', methods=['POST'])
def login():
    POST_USERNAME = str(request.form['username'])
    POST_PASSWORD = str(request.form['password'])

    Session = sessionmaker(bind=engine)
    s = Session()
    query = s.query(User).filter(User.username.in_([POST_USERNAME]), User.password.in_([POST_PASSWORD]))
    result = query.first()
    if result:
        global user
        user = POST_USERNAME
        session['logged_in'] = True
    else:
        flash('wrong password!')
    return home()

@app.route('/sign')
def sign():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup():

    POST_USERNAME = str(request.form['username'])
    POST_PASSWORD = str(request.form['password'])

    Session = sessionmaker(bind=engine)
    s = Session()

    user = User(POST_USERNAME, POST_PASSWORD)
    s.add(user)
    s.commit()

    session['logged_in'] = True
    session['false'] = True
    return home()



@app.route("/logout")
def logout():
    session['logged_in'] = False
    return home()

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)