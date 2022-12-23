from . import db #This will import from current package
from flask_login import UserMixin
from datetime import datetime #Allows the storing of the time of each card's creation
from sqlalchemy.sql import func#can be delted if you dont use time from it
#one to many uses foreign keys only
#db.model is a SQLALCHEMY MODEL
# class Deck(db.Model,UserMixin):
#     id = db.Column(db.Integer, primary_key=True)
#     Name = db.Column(db.String(300))
#     date = db.Column(db.DateTime(timezone=True),default=func.now())#func gets current date and time and stores it as a default value
#     #Store the foregin key in the child object for the parent, Classname(lower case).primarykey column name
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#     children_deck = db.relationship('Deck')
#     cards = db.relationship('Card')

class Deck(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(300),nullable=False)
    date = db.Column(db.DateTime(timezone=True),default=func.now())#
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    parent_id = db.Column(db.Integer, db.ForeignKey('deck.id'))#This is the foreign key for the parent deck
    children_deck = db.relationship('Deck',
                                    backref=db.backref('parent', remote_side=[id]),
                                    primaryjoin='Deck.parent_id == Deck.id')#This is the relationship for the child deck, the backref is the parent deck, the primaryjoin is the foreign key for the child deck
    cards = db.relationship('Card')

    def __repr__(self):
        return f"Deck('{self.name}','{self.children_deck}')"

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)#Primary key
    Question = db.Column(db.String(1000))
    Answer = db.Column(db.String(1000))
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    #[PUT INSIDE ANSWER?!?!]image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    date = db.Column(db.DateTime(timezone=True),default=func.now())#func gets current date and time and stores it as a default value
    #date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    #Store the foregin key in the child object for the parent, Classname(lower case).primarykey column name
    deck_id = db.Column(db.Integer, db.ForeignKey('deck.id'))
    #content = db.Column(db.Text, nullable=False)
    #user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # def __repr__(self):
    #     return f"User('{self.username}', '{self.email}', '{self.image_file}')"
    # def __repr__(self):
    #     return f"Post('{self.title}', '{self.date_posted}')"

class User(db.Model,UserMixin):
    """
    Class for the User in the database that is the primary table, that has a child class of deck and is a foreign key in decks class
    """
    #ID will be primary key
    id = db.Column(db.Integer,primary_key= True)
    username = db.Column(db.String(100), unique = True)
    email = db.Column(db.String(75),unique=True)
    password = db.Column(db.String(150))
    decks = db.relationship('Deck')#stores all the decks that the owner owns, in the parents class

    #ADD TIMEin utc from vid and check if they alll match desihnAND RE-EVULATE RELATIONSHIPS
    # def __repr__(self):
    #     return '<User %r>' % self.username
    def __repr__(self):
        return f"User('{self.id}', '{self.username}','{self.email}','{self.password}')"