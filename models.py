# models.py 
 
from app import db
 
 
class Artist(db.Model):
    __tablename__ = "artists"
 
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
 
    def __repr__(self):
        return "<Artist: {}>".format(self.name)
 
 
class Song(db.Model):
    """"""
    __tablename__ = "song"
 
    id = db.Column(db.Integer, primary_key=True)
    song = db.Column(db.String)
    mp3_file = db.Column(db.String)
 
    artist_id = db.Column(db.Integer, db.ForeignKey("artists.id"))
    artist = db.relationship("Artist", backref=db.backref(
        "song", order_by=id), lazy=True)
