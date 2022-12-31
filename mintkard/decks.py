from flask import Blueprint, render_template,request,url_for,redirect,flash,current_app
from . import db
from .models import User,Deck,Card
from flask_login import current_user,login_required
from datetime import datetime, timedelta 
from typing import List,Tuple

decks = Blueprint('decks', __name__)

class FlashcardManager:
    def __init__(self, user_id: int):
        self.user = User.query.get(user_id)


    '''returns a list of decks that the user owns'''
    def get_all_decks(self) -> List[Deck]:
        for deck in self.user.decks:
            print(deck)
        return

    '''returns a list of subdecks that the user owns'''
    def get_all_subdecks(self,user:User) -> List[Deck]:
        subdecks = []
        for deck in user.decks:
            subdecks.append(deck.children_deck)
        return subdecks

    '''returns a list of cards that the user owns'''
    def get_all_cards(self,user:User) -> List[Card]:
        cards = []
        for deck in user.decks:
            cards.append(deck.cards)
        return cards


    '''
    The following three function review_flashcards, is_card_due and review_deck are used to review the flashcards and are used and work together 
    alongside the update_stats in card class
    '''
    def review_flashcards(self, flashcards: List[Card]) -> List[Tuple[Card]]:
        reviewed_flashcards = []
        for flashcard in flashcards:
            print(flashcard.question)
            #send card to flask front end
            flashcard.update_stats()
            flashcard.last_reviewed = datetime.now()
            db.session.commit()
            reviewed_flashcards.append(flashcard)
        return reviewed_flashcards

    def is_card_due(self,flashcard:Card) -> bool:
        if flashcard.is_new == True:
            return True
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

    #This is the main thing that is called,
    def review_deck(self, deck_id) -> List[Tuple[Card, bool]]:#deck_id: int = None,deck: Deck = None if deck_id is not None: then find the deck else use the deck
        deck= Deck.query.get(deck_id)
        flashcards_to_review = []
        print('deck.id is',deck.id)
        for flashcard in deck.cards:
            print('flashcard is',flashcard.question)
            if self.is_card_due(flashcard):
                flashcards_to_review.append(flashcard)
        for subdeck in deck.children_deck:
            flashcards_to_review.extend(self.review_deck(subdeck.id))
        print('flashcards to review is ',flashcards_to_review)
        return self.review_flashcards(flashcards_to_review)

# with current_app.test_request_context():
#     # create the instance of the package within the blueprint
#     FManager = FlashcardManager(user_id)()
#app_context().push()
#manager = FlashcardManager(1)
# with current_app.app_context():
#     FManager = FlashcardManager(1)
#manager.review_deck(1)

'''
TO-DO in edit pages maybe
return redirect(url_for("login", next_page="/profile"))
'''

# def redirect_unauth():
#     '''
#     Redirects unauthenticated people to the login page
#     DELETE LATER MAYBE CHECK IF WORKS
#     '''
#     if not current_user.is_authenticated():
#         return redirect(url_for("login", next_page="/profile"))
#     else:
#         return None

@decks.route('/')
@decks.route('/home')
@login_required
def decks_route():
    '''
    This is the main homepage for the decks page, where all decks(set of cards) are shown and their subdecks
    They will have the option to study a deck, edit a deck, CHECK LATER HOW TO REDIRECT EDIT DECKS TO THE RIGHT DECK.
    The name is deck_route, because if its called decks it would cause an error as its the same name as the registered blueprint
    '''
    # with current_app.test_request_context():
    # # create the instance of the package within the blueprint
    #     FManager = FlashcardManager(1)
    #     FManager.get_all_cards()
    return render_template("decks.html")#,current_user=current_user)#Remove this later

@login_required
@decks.route('/browse')
def browse():
    return render_template("browse.html")

@login_required
@decks.route('/create',methods=['POST','GET'])
def create():
    '''
    Allows the user to create a new card
    '''
    return render_template("create.html")

@login_required
@decks.route('/study/<int:id>',methods=['GET','POST'])
def study(id):
    '''
    Allows the user to study new cards
    '''
    return render_template("study.html")

@login_required
@decks.route('/edit/<int:id>',methods=['GET','POST'])
def edit(id):
    '''
    Allows the user to edit existing cards
    '''
    return render_template("edit.html")

# @app.route("/user/<int:id>")
# def user_detail(id):
#MAKE EACH CARD HAVE A GET REQUEST WITH THE LINK CHANGING OF THE ID OF THGE CARD MAKING IT SHAREABELK???????????????????????!!!!!!!!
