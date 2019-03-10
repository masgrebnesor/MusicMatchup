# forms.py
 
from wtforms import Form, StringField, SelectField, FileField


class MusicSearchForm(Form):
    choices = [('Artist', 'Artist'),
               ('Song', 'Song')]
    select = SelectField('Search for music:', choices=choices)
    search = StringField('')

class SongForm(Form):
    artist = StringField('Artist')
    song = StringField('Song')
    mp3_file = FileField('Audio File')
