from flask import Blueprint, render_template,request,url_for,redirect,flash
from . import db
from .models import User,Deck,Card
from flask_login import current_user
import datetime
from typing import List,Tuple
decks = Blueprint('decks', __name__)


'''
TO-DO in edit pages maybe
return redirect(url_for("login", next_page="/profile"))
'''

class Card:
    def __init__(self,answer,question,quality:int,easiness_factor,interval,new:bool):
        self.question = question
        self.answer=answer
        self.newest_study = datetime.now()
        self.quality=quality #a quality is a number from 1 to 4
        self.easiness_factor = easiness_factor
        self.interval = interval
        self.is_new = is_new
        #remove the datime from the database?

    def study(self):
        '''Calculate the new interval based on the easiness factor, quality and interval.
        Reducing the minimum easiness factor's minimum of 1.3 would make it repeat alot more often, unnessesarily.
        '''
    
    #if it is new then we set the default variables
        if self.is_new:
            self.easiness_factor = 2.5
            self.interval = 1
            self.new=False
            return easiness_factor, interval
        elif self.quality <3:
            easiness = 2.5
            interval = 1
        else:
            if self.easiness_factor < 1.3:
                self.easiness_factor = 1.3
            elif self.easiness_factor > 2.5:
                self.easines_factor =2.5
            new_easiness_factor =  new_interval = 0
            self.easiness_factor = self.easiness_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
            new_interval = self.interval * new_easiness_factor
            self.easines_factor = new_easiness_factor
            self.interval = new_interval
            return new_E
        '''
        if the quality is more than 3 but the easiness factor is more than the
        the base limits we modify the easiness factor to make it stop it repeating too much or too little
        '''

        new_easiness_factor = new_interval = 0
        new_interval = interval * new_easiness_factor
        return new_easiness_factor, new_interval

    def update(self, quality: int):
        if self.is_new:
            self.easiness_factor = 2.5
            self.interval = 1
            self.is_new = False
        else:
            self.easiness_factor += (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
            self.easiness_factor = max(1.3, self.easiness_factor)
            self.interval = self.interval * self.easiness_factor
        self.quality = quality
        self.newest_study = datetime.now()


class Flashcard(Card):
    def __init__(self,question,answer,quality:int):
        super().__init__(question,answer,quality)
        self.quality = quality

#Check if this even works, the gaps thing is a bit fiddily on how gaps will be passed when created
class Fill_the_gaps(Card):
    def __init__(self,question,answer,gaps,quality:int):
        '''
        This will be another type of flashcard, a flashcard where answer is shown when reviewed, apart from some missing gaps indicated by the user
        '''
        #overrides the class inherited from, only put in items inherited
        super().__init__(question,answer,quality)

class Multi_choice(card):
    def __init__(self,question,answer,quality,choice:List):
        super().__init__(question,answer,quality)

class Deck:
    def __init__(self,name:str,sub_deck,flashcards:List,subdecks:List[Deck] = None):
        self.name = name
        self.flashcards = flashcards
        if subdecks:
            self.sub_decks = sub_deck
        else:
            self.sub_decks = []

class Sub_deck(sub_deck,flashcards):
    def __init__(self,name,flashcards):
        self.name = name
        self.sub_deck


def study_flashcard(flashcard:List[card]) -> List[Tuple[card,int]]:
    studied_flashcards = []
    #f as in flashcard, just to avoid errors/confusion with flashcard class
    for f in flashcards:
        result= flashcard.study()
        cards_studied.append((flashcard,result))
    return cards_studied


def study_deck(deck: Deck) -> List[Tuple[card,int]]:
    #if flashcard filters out the flashcard in the list, to only output flashcards that are due
    card_due = [f for f in deck.flashcards if review_due(flashcard)]
    card_due.extend(review_flashcards(Flashcards_to_Review))
    for subdeck in deck.subdecks:
        reviewed_flashcards.extend(review_deck(subdecks))

    return study_flashcard(card_due)

def study_due(flashcards:card,review,last_study_interval) -> bool:
    '''
    next_study is a integer where the quality is taken into account, and the last interval, for which a time is calculated for next study
    '''
    next_study = 0
    #alogirhtim here
    return reviewed_flashcards

def user_decks(user) -> List[Tuple[card,int]]:
    flashcards_studied = []
    for deck in user.decks:
        reviewed_flashcard.extend(review_deck(Deck))
    return flashcards_studied

#EXMAPLE USAGE
# mc_flashcard = multi_choice("What is the capital of France?", "Paris", ["Paris", "London", "Madrid"])
# flashcards = [mc_flashcard, flashcard("What is the capital of Japan?", "Tokyo")]
# deck = Deck("Country Capitals", flashcards)
# user_data = SQL QUERY TO EXTRACT ALL DECKS WITH CARDS AND SUBDECKS
# review_results = review_user(user_data)


# def redirect_unauth():
#     '''
#     Redirects unauthenticated people to the login page
#     DELETE LATER MAYBE CHECK IF WORKS
#     '''
#     if not current_user.is_authenticated():
#         return redirect(url_for("login", next_page="/profile"))
#     else:
#         return None

@login_required
@decks.route('/')
@decks.route('/home')
def decks_route():
    '''
    This is the main homepage for the decks page, where all decks(set of cards) are shown and their subdecks
    They will have the option to study a deck, edit a deck, CHECK LATER HOW TO REDIRECT EDIT DECKS TO THE RIGHT DECK.
    The name is deck_route, because if its called decks it would cause an error as its the same name as the registered blueprint
    '''
    return render_template("decks.html",curernt_user=current_user)

@login_required
@decks.route('/browse')
def browse():
    return render_template("browse.html")

@login_required
@decks.route('/create')
def create():
    '''
    Allows the user to create a new card
    '''
    return render_template("create.html")

@login_required
@decks.route('/study/<int:id>')
def study(id):
    '''
    Allows the user to study new cards
    '''
    return render_template("study.html")

@login_required
@decks.route('/edit/<int:id>')
def edit(id):
    '''
    Allows the user to edit existing cards
    '''
    return render_template("edit.html")

# @app.route("/user/<int:id>")
# def user_detail(id):
#MAKE EACH CARD HAVE A GET REQUEST WITH THE LINK CHANGING OF THE ID OF THGE CARD MAKING IT SHAREABELK???????????????????????!!!!!!!!
