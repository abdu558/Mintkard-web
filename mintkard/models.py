from . import db #This will import from current package
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta #Allows the storing of the time of each card's creation
from sqlalchemy.sql import func#can be delted if you dont use time from it
from typing import List,Tuple
from flask import Flask,current_app
from flask_login import UserMixin

#db = SQLAlchemy()

'''
This is the database, it's sqlalchemy
in future add classes and look at aqa and add all the OOP concepts e.g. encapsulation etc
WHY DOES ARD NOT HAVE USERMIXIN??? AND WHY DOES DECK HAVE IT
CHECK IF IMAGE STORING THIS WAY IS THE BEST WAY
CHECK IF IS_AUTHENTICATED FUNCTION AND GET_ID FUNCTION IS REQUIRED TO HAVE DESPIRE USERMIXIN BEING INHERITED????
'''


'''
INTEGRATION OF THE METHODS AND CALSSES IN THE MODELS FILE
NOTES:
NOT ADDING AN INIT METHOD
ADD TIME FUNC .NOW TO THE ALST STUDIED, WHENEVER QUALITY CHANGES
STUDY_DUE CAN HAVE EXPECTIONS FLASHED? AND PRINTED?
THE FILL THE GAPS FUNCTION? I HAVE NO IDEA HOW THAT WOULD WORK, KEEP IT LATER
ADD A ADD CARD GETTER AND SETTER? MAYBE EVEN UPDATE AND GET QUESTION,ANSWER GETTER AND SETTER
'''
class Deck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100),nullable=False)
    #description = db.Column(db.String(100))
    date = db.Column(db.DateTime(timezone=True),default=func.now())
    parent_id = db.Column(db.Integer, db.ForeignKey('deck.id'))#This is the foreign key for the parent deck
    children_deck = db.relationship('Deck',backref=db.backref('parent', remote_side=[id]),primaryjoin='Deck.parent_id == Deck.id')#This is the relationship for the child deck, the backref is the parent deck, the primaryjoin is the foreign key for the child deck
    cards = db.relationship('Card',lazy= True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    '''allows a string output'''
    def __repr__(self):
        return f"Deck('{self.name}','{self.children_deck}','{self.parent_id}')"

    def delete(self):
        pass

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)#Primary key
    question = db.Column(db.String(200))
    answer = db.Column(db.String(400))
    last_study = db.Column(db.DateTime(timezone=True))
    is_new = db.Column(db.Boolean, default=True)
    interval = db.Column(db.Integer)
    easiness_factor = db.Column(db.Integer)
    quality = db.Column(db.Integer)
    
    deck_id = db.Column(db.Integer, db.ForeignKey('deck.id'))#One to many relationship with decks
    
    def __repr__(self):
        return f"Card('{self.id}',{self.question}', '{self.answer}', '{self.deck_id}')"

    def delete(self):
        print('SUCCESS')

    def update_stats(self):# PASS IN quality
        '''
        This function is used on one card at a time
        Calculate the new interval based on the easiness factor, quality and interval.
        Reducing the minimum easiness factor below 1.3 would make it repeat a lot more often, unnecessarily.
        if the quality is more than 3 but the easiness factor is more than the
        the base limits we modify the easiness factor to make it stop it repeating too much or too little      
        '''
        print('!quality is',self.quality)
        if self.is_new:
            self.easiness_factor = 2.5
            self.interval = 1
            self.is_new=False
            return
            #return self.easiness_factor, self.interval
        self.quality = int(input('Enter the quality of the card: '))

        if self.quality <3:
            self.easiness_factor = 2.5
            self.interval = 1
            return
            #return self.easiness_factor, self.interval
        else:# If the easiness factor is outside the base limits, modify it to prevent it from repeating too much or too little 
            if self.easiness_factor < 1.3:
                self.easiness_factor = 1.3
            elif self.easiness_factor > 2.5:
                self.easiness_factor =2.5
            new_easiness_factor , new_interval = (0,0)
            new_easiness_factor += self.easiness_factor + (0.1 - (5 - self.quality) * (0.08 + (5 - self.quality) * 0.02))
            new_interval = self.interval * new_easiness_factor
            self.easiness_factor = new_easiness_factor
            self.interval = new_interval
            self.last_study = datetime.now()
            return
            #return self.interval,self.easiness_factor


class User(db.Model,UserMixin):
    """
    Class for the User in the database that is the primary table, that has a child class of deck and is a foreign key in decks class
    """
    #ID will be primary key
    id = db.Column(db.Integer,primary_key= True)
    username = db.Column(db.String(100), unique = True)
    email = db.Column(db.String(75),unique=True)
    password = db.Column(db.String(150))
    #Lazy  means that all subdecks and choldren will be loaded when a parent is loaded
    decks = db.relationship('Deck',backref = 'user_decks',lazy=True)#stores all the decks that the owner owns, in the parents class

    def __repr__(self):
        return f"User('{self.id}', '{self.username}','{self.email}','{self.password}')"




# class FlashcardManager:
#     def __init__(self, user_id: int,app):
#         self.app = app
#         with self.app.app_context():
#             self.user = User.query.get(user_id)


#     '''returns a list of decks that the user owns'''
#     def get_all_decks(self) -> List[Deck]:
#         for deck in self.user.decks:
#             print(deck)
#         return

#     '''returns a list of subdecks that the user owns'''
#     def get_all_subdecks(self,user:User) -> List[Deck]:
#         subdecks = []
#         for deck in user.decks:
#             subdecks.append(deck.children_deck)
#         return subdecks

#     '''returns a list of cards that the user owns'''
#     def get_all_cards(self,user:User) -> List[Card]:
#         cards = []
#         for deck in user.decks:
#             cards.append(deck.cards)
#         return cards


#     '''
#     The following three function review_flashcards, is_card_due and review_deck are used to review the flashcards and are used and work together 
#     alongside the update_stats in card class
#     '''
#     def review_flashcards(self, flashcards: List[Card]) -> List[Tuple[Card]]:
#         reviewed_flashcards = []
#         for flashcard in flashcards:
#             print(flashcard.question)
#             #send card to flask front end
#             flashcard.update_stats()
#             flashcard.last_reviewed = datetime.now()
#             db.session.commit()
#             reviewed_flashcards.append(flashcard)
#         return reviewed_flashcards

#     def is_card_due(self,flashcard:Card) -> bool:
#         if flashcard.is_new == True:
#             return True
#         try:
#             review_interval = timedelta(days=flashcard.interval)#converts int to time using datetime
#             return flashcard.last_reviewed + review_interval <= datetime.now()
#         except TypeError:
#             # Handle TypeError if it's not an integer
#             print("Error: Interval must be an integer")
#             return False
#         except ValueError:
#             # Handle ValueError if its a negative integer
#             print("Error: Interval must be a positive integer")
#             return False

#     #This is the main thing that is called,
#     def review_deck(self, deck_id) -> List[Tuple[Card, bool]]:#deck_id: int = None,deck: Deck = None if deck_id is not None: then find the deck else use the deck
#         deck= Deck.query.get(deck_id)
#         flashcards_to_review = []
#         print('deck.id is',deck.id)
#         for flashcard in deck.cards:
#             print('flashcard is',flashcard.question)
#             if self.is_card_due(flashcard):
#                 flashcards_to_review.append(flashcard)
#         for subdeck in deck.children_deck:
#             flashcards_to_review.extend(self.review_deck(subdeck.id))
#         print('flashcards to review is ',flashcards_to_review)
#         return self.review_flashcards(flashcards_to_review)



#deck1 = Deck(name='Geography',)
# result = db.session.execute("SELECT * FROM User")
# for row in result:
#     print(row)
# Create the decks
# current_app.app_context().push()
# deck1 = Deck(name='Deck 1', user_id=1)
# deck2 = Deck(name='Deck 2', user_id=1)
# db.session.add(deck1)
# db.session.add(deck2)
# db.session.commit()
# subdeck1 = Deck(name='Subdeck 1', user_id=1, parent_id=deck1.id)
# subdeck2 = Deck(name='Subdeck 2', user_id=1, parent_id=deck1.id)
# db.session.add(subdeck1)
# db.session.add(subdeck2)
# db.session.commit()

# # Create the cards
# card1 = Card(question='Question 1', answer='Answer 1', deck_id=deck1.id)
# card2 = Card(question='Question 2', answer='Answer 2', deck_id=deck1.id)
# card3 = Card(question='Question 3', answer='Answer 3', deck_id=deck2.id)
# card4 = Card(question='Question 4', answer='Answer 4', deck_id=deck2.id)
# card5 = Card(question='Question 5', answer='Answer 5', deck_id=subdeck1.id)
# card6 = Card(question='Question 6', answer='Answer 6', deck_id=subdeck1.id)
# card7 = Card(question='Question 7', answer='Answer 7', deck_id=subdeck2.id)
# card8 = Card(question='Question 8', answer='Answer 8', deck_id=subdeck2.id)

# # Add the decks and cards to the database

# db.session.add(card1)
# db.session.add(card2)
# db.session.add(card3)
# db.session.add(card4)
# db.session.add(card5)
# db.session.add(card6)
# db.session.add(card7)
# db.session.add(card8)
# db.session.commit()

# # print(deck1)
# # print(deck1.cards)
# # print(deck1.children_deck)
# # print(subdeck2.parent_id)
# manager = FlashcardManager(1)
# print(manager.get_all_decks())
#manager.review_deck(1)

#print(student1)




































# class Deck(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     Name = db.Column(db.String(300),nullable=False)
#     date = db.Column(db.DateTime(timezone=True),default=func.now())
#     image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#     parent_id = db.Column(db.Integer, db.ForeignKey('deck.id'))#This is the foreign key for the parent deck
#     children_deck = db.relationship('Deck',
#                                     backref=db.backref('parent', remote_side=[id]),
#                                     primaryjoin='Deck.parent_id == Deck.id')#This is the relationship for the child deck, the backref is the parent deck, the primaryjoin is the foreign key for the child deck
#     cards = db.relationship('Card')

#     def __repr__(self):
#         return f"Deck('{self.name}','{self.children_deck}','{self.parent_id}')"

# class Card(db.Model):
#     id = db.Column(db.Integer, primary_key=True)#Primary key
#     Question = db.Column(db.String(1000))
#     Answer = db.Column(db.String(1000))
#     image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
#     date = db.Column(db.DateTime(timezone=True),default=func.now())#func gets current date and time and stores it as a default value
#     #date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
#     #Store the foregin key in the child object for the parent, Classname(lower case).primarykey column name
#     deck_id = db.Column(db.Integer, db.ForeignKey('deck.id'))#One to many relationship with decks
#     #content = db.Column(db.Text, nullable=False)
#     #user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     # def __repr__(self):
#     #     return f"User('{self.username}', '{self.email}', '{self.image_file}')"
#     # def __repr__(self):
#     #     return f"Post('{self.title}', '{self.date_posted}')"


# class User(db.Model,UserMixin):
#     """
#     Class for the User in the database that is the primary table, that has a child class of deck and is a foreign key in decks class
#     """
#     #ID will be primary key
#     id = db.Column(db.Integer,primary_key= True)
#     username = db.Column(db.String(100), unique = True)
#     email = db.Column(db.String(75),unique=True)
#     password = db.Column(db.String(150))
#     decks = db.relationship('Deck')#stores all the decks that the owner owns, in the parents class


#     #ADD TIMEin utc from vid and check if they alll match desihnAND RE-EVULATE RELATIONSHIPS
#     # def __repr__(self):
#     #     return '<User %r>' % self.username
#     def __repr__(self):
#         return f"User('{self.id}', '{self.username}','{self.email}','{self.password}')"