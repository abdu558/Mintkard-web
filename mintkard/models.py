from . import db #This will import from current package
from flask_login import UserMixin

#one to many uses foreign keys only
class Deck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String('300'))
    date = db.Column(db.DateTime(timezone=True),default=func.now())#func gets current date and time and stores it as a default value
    #Store the foregin key in the child object for the parent, Classname(lower case).primarykey column name
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    cards = db.relationship('Card')

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)#Primary key
    Question = db.Column(db.String('1000'))
    Answer = db.Column(db.String('1000'))
    date = db.Column(db.DateTime(timezone=True),default=func.now())#func gets current date and time and stores it as a default value
    #Store the foregin key in the child object for the parent, Classname(lower case).primarykey column name
    deck_id = db.Column(db.Integer, db.ForeignKey('deck.id'))



class User(db.Model,UserMixin):
    """
    Class for the User in the database that is the primary table, that has a child class of deck and is a foreign key in decks class
    """
    id = db.Column(db.Integer,primary_key= True)
    email = db.Column(db.String(75),unique=True)
    password = db.Column(db.String(150))
    username = db.Column(db.String(100), unique = True)
    decks = db.relationship('Deck')#stores all the decks that the owner owns, in the parents class

    #ADD TIME AND RE-EVULATE RELATIONSHIPS