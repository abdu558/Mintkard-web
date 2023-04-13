from . import db #This will import from current package
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime #Allows the storing of the time of each card's creation
from sqlalchemy.sql import func #used in the 
from flask import Flask,current_app
from flask_login import UserMixin
import math

'''
backref allows accessing the realtionship object e.g. if in the deck object it had a backref deck. this would allow the card to do card.deck and now access the deck's info directly
'''

class Deck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100),nullable=False)
    description = db.Column(db.String(500))
    date = db.Column(db.DateTime(timezone=True),default=func.now())
    image_hash = db.Column(db.String, nullable=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('deck.id'))#This is the foreign key for the parent deck

    #reference for self referential/recurvisve relationship: https://docs.sqlalchemy.org/en/20/orm/self_referential.html
    children_deck = db.relationship('Deck',backref=db.backref('parent', remote_side=[id]),primaryjoin='Deck.parent_id == Deck.id')#This is the relationship for the child deck, the backref is the parent deck, the primaryjoin is the foreign key for the child deck
    cards = db.relationship('Card',lazy= True,cascade='all, delete-orphan',backref='deck')#cascade will delete all the cards in the deck if its deleted, and its subdecks/child decks (orphan)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(200))
    answer = db.Column(db.String(400))
    last_study = db.Column(db.DateTime(timezone=True))
    is_new = db.Column(db.Boolean, default=True)
    interval = db.Column(db.Integer)
    easiness_factor = db.Column(db.Integer)
    quality = db.Column(db.Integer)
    image_hash = db.Column(db.String, nullable=True)#new
    deck_id = db.Column(db.Integer, db.ForeignKey('deck.id'))#One to many relationship with decks
    

    def update_stats(self,quality):
        '''
        This function is used on one card at a time
        Calculate the new interval based on the easiness factor, quality and interval.
        Reducing the minimum easiness factor below 1.3 would make it repeat a lot more often, unnecessarily.
        if the quality is more than 3 but the easiness factor is more than the
        the base limits we modify the easiness factor to make it stop it repeating too much or too little      
        '''

        self.quality = quality
        self.last_study = datetime.now()
        if self.is_new:
            self.easiness_factor = 2.5
            self.interval = 1
            self.is_new=False
            return
        if self.quality <3:
            self.easiness_factor = 2.5
            self.interval = 1
            return
        else:
            # If the easiness factor is outside the base limits, modify it to prevent it from repeating too much or too little 
            if self.easiness_factor < 1.3:
                self.easiness_factor = 1.3
            elif self.easiness_factor > 2.5:
                self.easiness_factor =2.5
            new_easiness_factor , new_interval = (0,0)
            new_easiness_factor += self.easiness_factor + (0.1 - (5 - self.quality) * (0.08 + (5 - self.quality) * 0.02))


            #
            time = (self.last_study - datetime.now()).days
            new_interval = self.interval * new_easiness_factor
            if new_interval > 50:
            new_interval =  new_interval * math.exp(-time/(new_easiness_factor*10))
            self.easiness_factor = new_easiness_factor
            self.interval = new_interval

            db.session.commit()



class User(db.Model,UserMixin):
    """
    Class for the User in the database that is the primary table, that has a child class of deck and is a foreign key in decks class
    """
    id = db.Column(db.Integer,primary_key= True)
    username = db.Column(db.String(50), unique = True)
    email = db.Column(db.String(300),unique=True)
    password = db.Column(db.String(200))

    #Lazy  means that all subdecks and choldren will be loaded when a parent is loaded
    decks = db.relationship('Deck',backref = 'user_decks',lazy=True)#stores all the decks that the owner owns, in the parents class



