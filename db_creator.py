# db_creator.py
 
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
 
engine = create_engine('sqlite:///mymusicv2.db', echo=True)
Base = declarative_base()
 
 
class Artist(Base):
    __tablename__ = "artists"
 
    id = Column(Integer, primary_key=True)
    name = Column(String)
 
    def __repr__(self):
        return "{}".format(self.name)
 
 
class Song(Base):
    """"""
    __tablename__ = "song"
 
    id = Column(Integer, primary_key=True)
    song = Column(String)
    mp3_file = Column(String)
    rank = Column(Integer)

    artist_id = Column(Integer, ForeignKey("artists.id"))
    artist = relationship("Artist", backref=backref(
        "song", order_by=id))
 
# create tables
Base.metadata.create_all(engine)
