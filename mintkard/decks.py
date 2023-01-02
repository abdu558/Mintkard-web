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


    # '''returns a list of decks that the user owns'''
    # def get_all_decks(self) -> List[Deck]:
    #     root_decks = []
    #     for deck in self.user.decks:
    #         root_decks.append(deck)
    #     return

    # '''returns a list of subdecks that the user owns'''
    # def get_all_subdecks(self,user:User) -> List[Deck]:
    #     subdecks = []
    #     for deck in user.decks:
    #         subdecks.append(deck.children_deck)
    #     return subdecks

    '''returns a list of cards that the user owns'''
    def get_all_cards(self) -> List[Card]:
        cards = []
        #Does this get cards from subdecks, does self.user.decks show subdecks????!!?!?!
        for deck in self.user.decks:
            cards.append(deck.cards)
        return cards

    def get_all_decks(self,root_decks: List[Deck]) -> List[Deck]:
        all_decks = []
        for root_deck in root_decks:
            all_decks.extend(self.get_all_decks_recursive(root_deck))
        return all_decks

    def get_all_decks_recursive(self,root_deck: Deck) -> List[Deck]:
        all_decks = [root_deck]
        for subdeck in root_deck.children_deck:
            all_decks.extend(self.get_all_decks_recursive(subdeck))
        return all_decks




    '''
    The following three function review_flashcards, is_card_due and review_deck are used to review the flashcards and are used and work together 
    alongside the update_stats in card class
    '''
    def review_flashcards(self, flashcards: List[Card]) -> List[Tuple[Card]]:
        reviewed_flashcards = []
        for flashcard in flashcards:
        #     print(flashcard.question)
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
        #print('deck.id is',deck.id)
        for flashcard in deck.cards:
            #print('flashcard is',flashcard.question)
            if self.is_card_due(flashcard):
                flashcards_to_review.append(flashcard)
        for subdeck in deck.children_deck:
            flashcards_to_review.extend(self.review_deck(subdeck.id))
        #print('flashcards to review is ',flashcards_to_review)
        return self.review_flashcards(flashcards_to_review)


current_app.app_context().push()
# db.session.execute('DELETE * FROM Deck')
# db.session.commit()
#print(current_user)
#fmanager = FlashcardManager(current_user.id, current_app)


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

#fmanager.review_deck(1)
#root_decks = Deck.query.filter_by(parent_id=None).all()




# print(isinstance(root_decks, list))
# all_decks = fmanager.get_all_decks(root_decks)
# for deck in all_decks:
#     print(deck.name)
#print(root_decks[0])


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

'''
This is the main homepage for the decks page, where all decks(set of cards) are shown and their subdecks
They will have the option to study a deck, edit a deck, CHECK LATER HOW TO REDIRECT EDIT DECKS TO THE RIGHT DECK.
The name is deck_route, because if its called decks it would cause an error as its the same name as the registered blueprint
'''



@decks.route('/home')
@decks.route('/',methods=['GET','POST'])
@login_required
def decks_route():
    '''
    by default, its get so if a post request is going to be recived in the route, it must be specified a post, and also a get to get the page request
    there is no need to put methods in both routes, the methods will apply to both routes if specified in one.
    having two routes means that if somenes visits any of the two then it will redirect to the same page
    login_required means that the user must be logged in, if the use isnt then they are redirected to login page, where they can also select to register an account if they are new
    the login page is specified as the redirect in the __init__ file where the route auth.login is configured.

    root deck is a deck without a parent deck, just like a tree graph where a root can have children but cant have a parent
    '''
    print('helloo')
    root_decks = Deck.query.filter_by(parent_id=None,user_id =current_user.id).all()
    #if request.method == 'POST':
    if request.form.get('add_deck'):
        num_of_decks = len(root_decks)
        num_of_decks = 'Deck' + str(num_of_decks)
        new_deck = Deck(name='DECKS',user_id=current_user.id)
        db.session.add(new_deck)
        db.session.commit()
        
        root_decks = Deck.query.filter_by(parent_id=None,user_id=current_user.id).all()
        return render_template("decks.html",root_decks = root_decks)
    if request.form.get('delete_deck'):
        
        try:
            deck_id = request.form.get('delete_deck')
        except:
            flash('Deck with id {} not found'.format(deck_id), category='danger')
        
        deck_to_delete = Deck.query.get_or_404(deck_id)
        db.session.delete(deck_to_delete)
        db.session.commit()

        root_decks = Deck.query.filter_by(parent_id=None,user_id=current_user.id).all()
        return render_template("decks.html",root_decks= root_decks)
    #ADD THIS AND A FORM AND A BUTTON TO THE DELTE REQUEST.

    return render_template("decks.html",root_decks= root_decks)#,current_user=current_user)#Remove this later

@login_required
@decks.route('/stats')
def stats():

    pass

@login_required
@decks.route('/browse')
def browse():
    #all_cards = fmanager.get_all_cards(user)
    return render_template("browse.html",all_cards)

#ADD AN ID TO IT SO IF A USER PRESSES STUDY IT WOULD SEND A ID, HOW DO YOU AUTOMAITCALLY GENERATE AN ID
@login_required
@decks.route('/create',methods=['POST','GET'])
def create():
    '''
    Allows the user to create a new card
    '''
    if request.method == 'POST':
        if request.form.get('question') and request.form.get('answer') and request.form.get('deck_id'):
            question = request.form.get('question')
            answer = request.form.get('answer')


            #perform check here??!!?

            #paramzlied sql query

            card = Card(question = question,answer= answer,deck_id =request.form['deck_id'])
            db.session.add(card)
            db.session.commit()
    return render_template("create.html")

#study entire deck, where there is a redirect to study each card
@login_required
@decks.route('/study-deck/<int:deck_id>')
def study_deck(deck_id):

    deck = Deck.query.get(deck_id)
    #print('Revise deck')
    return redirect(url_for('deck.decks_route'), permanent=True)

#study one card
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

#edit entire deck
@login_required
@decks.route('/edit-deck/<int:deck_id>')
def edit_deck(deck_id):
    current_deck = Deck.query.filter_by(parent_id=None,id=deck_id).first()#.all()
    if request.method== 'POST':
        title = request.form.get('question')
        answer = request.form.get('answer')
        flash('Deck has been updated',category='success')
        return redirect(url_for('decks_route'),code=301)#301 is a permanent redirect

    # put the infomraiton has a placeholder and check if there is a change, then check how to update deck info
    return render_template("edit_deck.html",deck=current_deck)
    # print(deck_id)
    # deck_to_delete = Deck.query.get(deck_id)#query.get_or_404
    # #if deck_to_delete:
    # db.session.delete(deck_to_delete)
    # db.session.commit()
    # #else:
    # #flash('Deck with id {} not found'.format(deck_id), category='danger')
#deletes entire deck

# @login_required
# @decks.route('/delete-deck/<int:deck_id>')
# def delete_deck(deck_id):
#     print('WORKING?')
#     deck_to_delete = Deck.query.get_or_404(deck_id)
#     db.session.delete(deck_to_delete)
#     db.session.commit()
#     return redirect(url_for('decks.decks_route'), code=301)#301 is a permanent redirect

#edits individual cards
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
