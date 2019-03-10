from app import app
from db_setup import init_db, db_session
from forms import MusicSearchForm, SongForm
from flask import flash, render_template, request, redirect
from models import Song, Artist
from tables import Results

init_db()

from flask import Flask
from flask import Flask, flash, redirect, render_template, request, session, abort
import os
from sqlalchemy.orm import sessionmaker
from tabledef import *
import uuid
from flask_login import LoginManager
from werkzeug.utils import secure_filename
import random
import webbrowser

songone = Song()
songtwo = Song()

engine = create_engine('sqlite:///tutorial.db', echo=True)

user = ""

@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('index.html')
    else:
        files = os.listdir('static/music')
        if len(files) != 0:
            index1 = random.randrange(0, len(files))
            index2 = random.randrange(0, len(files))
            if (len(files) > 1):
                while index1 == index2:
                    index2 = random.randrange(0, len(files))

            global songone
            global songtwo
            songone = song_lookup(files[index1])
            songtwo = song_lookup(files[index2])

            print(songone)
            print(songtwo)

            return render_template('index.html', user=user, song1="static/music/" + files[index1], song2="static/music/" + files[index2])
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

#implement elo ranking system of song 1 vs song 2, start with 1600
@app.route('/song1')
def song1():
    s1 = songone.rank
    s2 = songone.rank

    q1 = 10**(s1/400)
    q2 = 10**(s2/400)

    e1 = q1 / (q1+q2)
    e2 = q2 / (q1+q2)

    s1 = s1 + 32*e2
    s2 = s2 - 32*e2

    print(s1)

    return home()

@app.route('/song2')
def song2():
    s1 = songone.rank
    s2 = songtwo.rank

    q1 = 10 ** (s1 / 400)
    q2 = 10 ** (s2 / 400)

    e1 = q1 / (q1 + q2)
    e2 = q2 / (q1 + q2)

    s1 = s1 - 32 * e1
    s2 = s2 + 32 * e1

    return home()

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


@app.route('/search', methods=['GET', 'POST'])
def index():
    search = MusicSearchForm(request.form)
    if request.method == 'POST':
        return search_results(search)

    return render_template('indexmusic.html', form=search)

def song_lookup(search_string):
    print(search_string)
    print(Song.mp3_file)
    qry = db_session.query(Song).filter(
        Song.mp3_file.contains(search_string))
    song = qry.first()
    return song

@app.route('/results')
def search_results(search):
    results = []
    search_string = search.data['search']

    if search_string:
        if search.data['select'] == 'Artist':
            qry = db_session.query(Song, Artist).filter(
                Artist.id == Song.artist_id).filter(
                Artist.name.contains(search_string))
            results = [item[0] for item in qry.all()]
        elif search.data['select'] == 'Song':
            qry = db_session.query(Song).filter(
                Song.title.contains(search_string))
            results = qry.all()
        else:
            qry = db_session.query(Song)
            results = qry.all()
    else:
        qry = db_session.query(Song)
        results = qry.all()

    if not results:
        flash('No results found!')
        return redirect('/search')
    else:
        # display results
        table = Results(results)
        table.border = True
        return render_template('results.html', table=table)


@app.route('/new_album', methods=['GET', 'POST'])
def new_song():
    """
    Add a new album
    """
    form = SongForm(request.form)

    if request.method == 'POST' and form.validate():
        # save the album
        song = Song()
        save_changes(song, form, new=True)
        flash('Song uploaded successfully!')
        return redirect('/upload')

    return render_template('new_album.html', form=form) #should be new_song, not new_album


def save_changes(song, form, new=False):
    """
    Save the changes to the database
    """
    # Get data from form and assign it to the correct attributes
    # of the SQLAlchemy table object
    artist = Artist()
    artist.name = form.artist.data

    song.artist = artist
    song.song = form.song.data
    song.mp3_file = form.mp3_file.data
    song.rank = 1600

    if new:
        # Add the new album to the database
        db_session.add(song)

    # commit the data to the database
    db_session.commit()


@app.route('/upload')
def upload_file():
    return render_template('upload.html')


@app.route('/uploader', methods=['GET', 'POST'])
def upload_file2():
    if request.method == 'POST':
        f = request.files['file']
        f.save('static/music/' + secure_filename(f.filename))
        return home()


@app.route('/item/<int:id>', methods=['GET', 'POST'])
def edit(id):
    qry = db_session.query(Song).filter(
        Song.id == id)
    song = qry.first()

    if song:
        form = SongForm(formdata=request.form, obj=song)
        if request.method == 'POST' and form.validate():
            # save edits
            save_changes(song, form)
            flash('Song updated successfully!')
            return redirect('/search')
        return render_template('edit_album.html', form=form) #edit_song, not edit_album
    else:
        return 'Error loading #{id}'.format(id=id)


@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
    """
    Delete the item in the database that matches the specified
    id in the URL
    """
    qry = db_session.query(Song).filter(
        Song.id == id)
    song = qry.first()

    if song:
        form = SongForm(formdata=request.form, obj=song)
        if request.method == 'POST' and form.validate():
            # delete the item from the database
            db_session.delete(song)
            db_session.commit()

            flash('Song deleted successfully!') #this is so sick oh my gosh -caroline (p.s. omg i want it where is it from)
            return redirect('/')
        return render_template('delete_album.html', form=form) #song, not album
    else:
        return 'Error deleting #{id}'.format(id=id)


if __name__ == "__main__":
    app.run()
