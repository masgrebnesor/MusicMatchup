from flask_table import Table, Col, LinkCol
 
class Results(Table):
    id = Col('Id', show=False)
    artist = Col('Artist')
    song = Col('Song')
    #mp3_file = Col('Audio File')
    edit = LinkCol('Edit', 'edit', url_kwargs=dict(id='id'))
    delete = LinkCol('Delete', 'delete', url_kwargs=dict(id='id'))
