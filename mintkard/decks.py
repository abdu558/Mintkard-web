from flask import Blueprint, render_template,request,url_for,redirect,flash,current_app#,push_app_context
from . import db
from .models import User,Deck,Card#,db
from flask_login import current_user,login_required
from datetime import datetime, timedelta 
from typing import List,Tuple

decks = Blueprint('decks', __name__)

class FlashcardManager:
    def __init__(self, user_id: int,app):
        print('FlashcardManager __init__ called')
        self.app = app
        current_app.app_context().push()
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
            flashcard.last_study = datetime.now()
            db.session.commit()
            reviewed_flashcards.append(flashcard)
        return reviewed_flashcards

    def is_card_due(self,flashcard:Card) -> bool:
        if flashcard.is_new == True:
            return True
        try:
            review_interval = timedelta(days=flashcard.interval)#converts int to time using datetime
            return flashcard.last_study + review_interval <= datetime.now()
        except TypeError:
            # Handle TypeError if it's not an integer
            print("Error: Interval must be an integer")
            return False
        except ValueError:
            # Handle ValueError if its a negative integer
            print("Error: Interval must be a positive integer")
            return False

    #This is the main thing that is called,
    def review_deck(self, deck_id_or_deck) -> List[Tuple[Card, bool]]:#deck_id: int = None,deck: Deck = None if deck_id is not None: then find the deck else use the deck
        if isinstance(deck_id_or_deck, int):#Polymorphism
            deck= Deck.query.get(deck_id_or_deck)
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


current_app.app_context().push()

fmanager = FlashcardManager(1, current_app)
deck1 = Deck(name='Deck 1', user_id=1)
deck2 = Deck(name='Deck 2', user_id=1)
db.session.add(deck1)
db.session.add(deck2)
db.session.commit()
subdeck1 = Deck(name='Subdeck 1', user_id=1, parent_id=deck1.id)
subdeck2 = Deck(name='Subdeck 2', user_id=1, parent_id=deck1.id)
db.session.add(subdeck1)
db.session.add(subdeck2)
db.session.commit()

# Create the cards
card1 = Card(question='Question 1', answer='Answer 1', deck_id=deck1.id)
card2 = Card(question='Question 2', answer='Answer 2', deck_id=deck1.id)
card3 = Card(question='Question 3', answer='Answer 3', deck_id=deck2.id)
card4 = Card(question='Question 4', answer='Answer 4', deck_id=deck2.id)
card5 = Card(question='Question 5', answer='Answer 5', deck_id=subdeck1.id)
card6 = Card(question='Question 6', answer='Answer 6', deck_id=subdeck1.id)
card7 = Card(question='Question 7', answer='Answer 7', deck_id=subdeck2.id)
card8 = Card(question='Question 8', answer='Answer 8', deck_id=subdeck2.id)

# Add the decks and cards to the database

db.session.add(card1)
db.session.add(card2)
db.session.add(card3)
db.session.add(card4)
db.session.add(card5)
db.session.add(card6)
db.session.add(card7)
db.session.add(card8)
db.session.commit()
fmanager.review_deck(1)

#decks = Blueprint('decks', __name__)

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
    if request.method =='POST':
        if request.form.get('add_deck'):
            new_deck = request.form.get('add_deck')
            Deck = Deck(name= '')#find largest deck id and add 1)

        if request.form.get('delete_deck'):
            pass

        if request.form.get('edit'):
            redirect('')
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
@decks.route('/create/<int:id>',methods=['POST','GET'])
def create(id):
    '''
    Allows the user to create a new card
    '''
    if request.method == 'POST':
        if request.form.get('question') and request.form.get('answer'):
            question = request.form.get('question')
            answer = request.form.get('answer')

            #perform check here??!!?

            #paramzlied sql query

            card = Card(question = question,answer= answer,deck_id =id)
            db.session.add(card)
            db.session.commit()
    return render_template("create.html")

@login_required
@decks.route('/study/<int:id>',methods=['GET','POST'])
def study(id):
    '''
    Allows the user to study new cards
    '''
    if request.method == 'POST':
        if request.form.get('quality'):
            question = request.form.get('quaity')

    

    return render_template("study.html")

@login_required
@decks.route('/edit/<int:id>',methods=['GET','POST'])
def edit(id):
    '''
    Allows the user to edit existing cards
    '''
    if request.method == 'POST':
        if request.method.get('question') and request.method.get('answer'):
            Card = card.update(question=question,answer=answer)
            #db.commit ???
    return render_template("edit.html")

# @app.route("/user/<int:id>")
# def user_detail(id):
#MAKE EACH CARD HAVE A GET REQUEST WITH THE LINK CHANGING OF THE ID OF THGE CARD MAKING IT SHAREABELK???????????????????????!!!!!!!!
