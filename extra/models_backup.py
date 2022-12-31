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

'''
This is the database, it's sqlalchemy
in future add classes and look at aqa and add all the OOP concepts e.g. encapsulation etc
WHY DOES ARD NOT HAVE USERMIXIN??? AND WHY DOES DECK HAVE IT
CHECK IF IMAGE STORING THIS WAY IS THE BEST WAY
CHECK IF IS_AUTHENTICATED FUNCTION AND GET_ID FUNCTION IS REQUIRED TO HAVE DESPIRE USERMIXIN BEING INHERITED????
'''

class Deck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100),nullable=False)
    date = db.Column(db.DateTime(timezone=True),default=func.now())
    parent_id = db.Column(db.Integer, db.ForeignKey('deck.id'))#This is the foreign key for the parent deck
    children_deck = db.relationship('Deck',
                                    backref=db.backref('parent', remote_side=[id]),
                                    primaryjoin='Deck.parent_id == Deck.id')#This is the relationship for the child deck, the backref is the parent deck, the primaryjoin is the foreign key for the child deck
    cards = db.relationship('Card')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    def __repr__(self):
        return f"Deck('{self.name}','{self.children_deck}','{self.parent_id}')"

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)#Primary key
    question = db.Column(db.String(200))
    answer = db.Column(db.String(400))
    last_study = db.Column(db.DateTime)
    is_new = db.Column(db.Boolean)
    interval = db.Column(db.Integer)
    easiness_factor = db.Column(db.Integer)
    quality = db.Column(db.Integer)
    deck_id = db.Column(db.Integer, db.ForeignKey('deck.id'))#One to many relationship with decks
    
    def __repr__(self):
        return f"Card('{self.question}', '{self.answer}', '{self.id_deck}')"



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

    def __repr__(self):
        return f"User('{self.id}', '{self.username}','{self.email}','{self.password}')"





