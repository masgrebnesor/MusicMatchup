from app import app
from db_setup import init_db, db_session
from forms import MusicSearchForm, AlbumForm
from flask import flash, render_template, request, redirect
from models import Album
from models import Album, Artist
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

engine = create_engine('sqlite:///tutorial.db', echo=True)

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


@app.route('/search', methods=['GET', 'POST'])
def index():
    search = MusicSearchForm(request.form)
    if request.method == 'POST':
        return search_results(search)

    return render_template('indexmusic.html', form=search)


@app.route('/results')
def search_results(search):
    results = []
    search_string = search.data['search']

    if search_string:
        if search.data['select'] == 'Artist':
            qry = db_session.query(Album, Artist).filter(
                Artist.id == Album.artist_id).filter(
                Artist.name.contains(search_string))
            results = [item[0] for item in qry.all()]
        elif search.data['select'] == 'Album':
            qry = db_session.query(Album).filter(
                Album.title.contains(search_string))
            results = qry.all()
        elif search.data['select'] == 'Publisher':
            qry = db_session.query(Album).filter(
                Album.publisher.contains(search_string))
            results = qry.all()
        else:
            qry = db_session.query(Album)
            results = qry.all()
    else:
        qry = db_session.query(Album)
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
def new_album():
    """
    Add a new album
    """
    form = AlbumForm(request.form)

    if request.method == 'POST' and form.validate():
        # save the album
        album = Album()
        save_changes(album, form, new=True)
        flash('Album created successfully!')
        return redirect('/search')

    return render_template('new_album.html', form=form)


def save_changes(album, form, new=False):
    """
    Save the changes to the database
    """
    # Get data from form and assign it to the correct attributes
    # of the SQLAlchemy table object
    artist = Artist()
    artist.name = form.artist.data

    album.artist = artist
    album.title = form.title.data
    album.release_date = form.release_date.data
    album.publisher = form.publisher.data
    album.media_type = form.media_type.data
    album.mp3_file = form.mp3_file.data

    if new:
        # Add the new album to the database
        db_session.add(album)

    # commit the data to the database
    db_session.commit()


# new code from arushi starts here
@app.route('/upload')
def upload_file():
    return render_template('upload.html')


@app.route('/uploader', methods=['GET', 'POST'])
def upload_file2():
    if request.method == 'POST':
        f = request.files['file']
        f.save('music/' + secure_filename(f.filename))
        return home()


# new code from arushi ends here
@app.route('/item/<int:id>', methods=['GET', 'POST'])
def edit(id):
    qry = db_session.query(Album).filter(
        Album.id == id)
    album = qry.first()

    if album:
        form = AlbumForm(formdata=request.form, obj=album)
        if request.method == 'POST' and form.validate():
            # save edits
            save_changes(album, form)
            flash('Album updated successfully!')
            return redirect('/search')
        return render_template('edit_album.html', form=form)
    else:
        return 'Error loading #{id}'.format(id=id)


@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
    """
    Delete the item in the database that matches the specified
    id in the URL
    """
    qry = db_session.query(Album).filter(
        Album.id == id)
    album = qry.first()

    if album:
        form = AlbumForm(formdata=request.form, obj=album)
        if request.method == 'POST' and form.validate():
            # delete the item from the database
            db_session.delete(album)
            db_session.commit()

            flash('Album deleted successfully!')
            return redirect('/')
        return render_template('delete_album.html', form=form)
    else:
        return 'Error deleting #{id}'.format(id=id)


if __name__ == "__main__":
    app.run()
