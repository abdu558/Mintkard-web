from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta #Allows the storing of the time of each card's creation
from sqlalchemy.sql import func#can be delted if you dont use time from it
from typing import List,Tuple
from flask import Flask
from flask_login import UserMixin


db = SQLAlchemy()
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
db.init_app(app)
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
    date = db.Column(db.DateTime(timezone=True),default=func.now())
    parent_id = db.Column(db.Integer, db.ForeignKey('deck.id'))#This is the foreign key for the parent deck
    children_deck = db.relationship('Deck',backref=db.backref('parent', remote_side=[id]),primaryjoin='Deck.parent_id == Deck.id')#This is the relationship for the child deck, the backref is the parent deck, the primaryjoin is the foreign key for the child deck
    cards = db.relationship('Card')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    '''allows a string output'''
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
        return f"Card('{self.id}',{self.question}', '{self.answer}', '{self.deck_id}')"

    def study(self):
        '''
        This function is used on one card at a time
        Calculate the new interval based on the easiness factor, quality and interval.
        Reducing the minimum easiness factor below 1.3 would make it repeat a lot more often, unnecessarily.
        if the quality is more than 3 but the easiness factor is more than the
        the base limits we modify the easiness factor to make it stop it repeating too much or too little      
        '''
        if self.is_new:
            self.easiness_factor = 2.5
            self.interval = 1
            self.is_new=False
            return self.easiness_factor, self.interval
        elif self.quality <3:
            self.easiness_factor = 2.5
            self.interval = 1
            return self.easiness_factor, self.interval
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
            self.last_reviewed = datetime.now()
            return self.interval,self.easiness_factor


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

class FlashcardManager:
    def __init__(self, user_id: int):
        self.user = User.query.get(user_id)

    def review_flashcards(self, flashcards: List[Card]) -> List[Tuple[Card, int]]:
        reviewed_flashcards = []
        for flashcard in flashcards:
            result = flashcard.study()
            flashcard.last_reviewed = datetime.now()
            db.session.commit()
            reviewed_flashcards.append((flashcard, result))
        return reviewed_flashcards

    def is_card_due(self,flashcard:Card) -> bool:
        try:
            review_interval = timedelta(days=flashcard.interval)#converts int to time using datetime
            return flashcard.last_reviewed + review_interval <= datetime.now()
        except TypeError:
            # Handle TypeError if it's not an integer
            print("Error: Interval must be an integer")
            return False
        except ValueError:
            # Handle ValueError if its a negative integer
            print("Error: Interval must be a positive integer")
            return False

    def review_deck(self, deck_id: int,deck) -> List[Tuple[Card, bool]]:
        deck = Deck.query.get(deck_id)
        flashcards_to_review = [flashcard for flashcard in deck.flashcards if self.is_card_due(flashcard)]
        for subdeck in deck.children_deck:
            flashcards_to_review.extend(self.review_deck(subdeck.id))
        return self.review_flashcards(flashcards_to_review)

        

app.app_context().push()
#db.create_all()
#student1 = User(username='bodb22',email='kadaa@gmail.com',password='jimtmmy')    
#db.session.add(student1)
#db.session.commit()
#deck1 = Deck(name='Geography',)

print(student1)

    

# class FlashcardManager:
#     def __init__(self, user_id: int):
#         self.user = User.query.get(user_id)

#     def review_flashcards(self, flashcards: List[IFlashcard]) -> List[Tuple[IFlashcard, bool]]:
#         reviewed_flashcards = []
#         for flashcard in flashcards:
#             result = flashcard.review()
#             flashcard.last_reviewed = datetime.now()
#             db.session.commit()
#             reviewed_flashcards.append((flashcard, result))
#         return reviewed_flashcards

#     def review_due(self, flashcard: IFlashcard) -> bool:
#         review_interval = timedelta(days=1)  # Review flashcards every day
#         return flashcard.last_reviewed + review_interval <= datetime.now()

#     def review_deck(self, deck_id: int) -> List[Tuple[IFlashcard, bool]]:
#         deck = Deck.query.get(deck_id)
#         flashcards_to_review = [flashcard for flashcard in deck.flashcards if self.review_due(flashcard)]
#         return self.review_flashcards(flashcards_to_review)

