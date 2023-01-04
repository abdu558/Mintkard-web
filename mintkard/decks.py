from flask import Blueprint, render_template,request,url_for,redirect,flash,current_app,g
from . import db
from .models import User,Deck,Card#,db
from flask_login import current_user,login_required
from datetime import datetime, timedelta 
from typing import List,Tuple
import requests

decks = Blueprint('decks', __name__)

class FlashcardManager:
    def __init__(self,user_id:int,app):
        self.app = app
        self.user = User.query.get(user_id)



    '''returns a list of cards that the user owns'''
    def get_all_cards(self) -> List[Card]:

        cards = []
        for deck in self.user.decks:
            cards.extend(self.get_cards_from_deck(deck))
        return cards

    def get_cards_from_deck(self,deck: Deck) -> List[Card]:
        cards = deck.cards#gets the cards in the currrent deck, but cards in child_decks are not collected yet
        for child_deck in deck.children_deck:
            cards.extend(self.get_cards_from_deck(child_deck))
        return cards

    '''
    The two methods above work together to get all the cards in a tree, so get_all_cards (first method) will iterate throught each deck
    then it will pass one root deck to the get_cards_from_deck which does a tree traversal by calling itself recursively on each child deck
    This means that the function will visit the nodes in a depth first order from the root node to the last decks in the bottom, the leaf nodes
    without any children.
    All the cards get added to the  
    This is used in the browse cards route
    '''


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
    # def merge_sort(items):
    #     if len(items) <= 1:
    #         return items

    #     middle_index = len(items) // 2
    #     left_items = items[:middle_index]
    #     right_items = items[middle_index:]

    #     left_items = merge_sort(left_items)
    #     right_items = merge_sort(right_items)

    #     return merge(left_items, right_items)

    # def merge(left_items, right_items):
    #     sorted_items = []

    #     left_index = 0
    #     right_index = 0

    #     while left_index < len(left_items) and right_index < len(right_items):
    #         if left_items[left_index] <= right_items[right_index]:
    #             sorted_items.append(left_items[left_index])
    #             left_index += 1
    #         else:
    #             sorted_items.append(right_items[right_index])
    #             right_index += 1

    #     sorted_items.extend(left_items[left_index:])
    #     sorted_items.extend(right_items[right_index:])

    #     return sorted_items

    def review_flashcards(self, flashcards: List[Card]) -> List[Tuple[Card]]:
        reviewed_flashcards = []

        # flashcards_to_sort = []
        # flashcards.extend(flashcards_to_sort)
        # for flashcard in flashcards:
        #     if flashcard.is_new == True:
        #         continue
        #     else:
        #         flashcards_to_sort.append(flashcard)
        #         flashcards.remove(flashcard)
        
        #flashcards_to_sort = merge_sort(flashcards_to_sort)
        #flashcards.extend(flashcards_to_sort) # puts both of them back

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
        #print('deck.id is',deck.id)
        for flashcard in deck.cards:
            #print('flashcard is',flashcard.question)
            if self.is_card_due(flashcard):
                flashcards_to_review.append(flashcard)
        for subdeck in deck.children_deck:
            flashcards_to_review.extend(self.review_deck(subdeck.id))
        #print('flashcards to review is ',flashcards_to_review)
        return self.review_flashcards(flashcards_to_review)


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

#Globally initlize flashcard mana
@decks.before_request
def before_request():
    '''Globally initlise flashcard manager, will be accessed as g.fmanager in all routes in the decks blueprint'''
    g.fmanager = FlashcardManager(user_id=current_user.id, app=current_app)

# deck_id_a=8
# result = db.session.execute(f"SELECT user_id FROM deck WHERE id={deck_id_a}")
# card_userid=result.fetchone()[0]
# print(card_userid)
def user_owned_card(card_id):
    '''Returns true if the user does own the card, false if the user does not, preventing unauthorised access'''
    result = db.session.execute("""
        SELECT deck.user_id
        FROM card card
        INNER JOIN deck deck ON card.deck_id = deck.id
        WHERE card.id = {}
    """.format(card_id))
    if result.fetchone()[0] == current_user.id:
        return True
    return False
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

    return render_template("decks.html",root_decks= root_decks)#,current_user=current_user)#Remove this later

@login_required
@decks.route('/stats')
def stats():
# Number of decks: You can count the number of rows in the Deck table to get the total number of decks.
# Number of cards: You can count the number of rows in the Card table to get the total number of cards.
# Average number of cards per deck: You can divide the total number of cards by the total number of decks to get the average number of cards per deck.
# Date of last study: You can use the last_study column in the Card table to find the date of the last study for each card.
# Percentage of new cards: You can use the is_new column in the Card table to determine the percentage of cards that are new.
# Average interval: You can use the interval column in the Card table to calculate the average interval between study sessions for all of the cards.
# Average easiness factor: You can use the easiness_factor column in the Card table to calculate the average easiness factor for all of the cards.
# Average quality: You can use the quality column in the Card table to calculate the average quality of all of the cards.
    return render_template("stats.html")

@login_required
@decks.route('/browse')
def browse():

    # if request.form.get('edit_card'):
    #     try:
    #         card_id =  request.form['edit_deck']
    #     except:
    #         flash('card with id {} not found'.format(card_id), category='danger')

    
    #     card_to_edit = Deck.query.get_or_404(card_id)
    #     db.session.delete(card_to_edit)
    #     db.session.commit()

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

    try:
        all_cards = g.fmanager.get_all_cards()
    except Exception as e:
        flash('Error locating decks: {}'.format(e),category='danger')
    print(all_cards)

    return render_template("browse.html",cards =all_cards)

#ADD AN ID TO IT SO IF A USER PRESSES STUDY IT WOULD SEND A ID, HOW DO YOU AUTOMAITCALLY GENERATE AN ID
#maybe make the options show all the decks and subdecks, if a user wants to put something theyl put it inside the subdeck
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
            deck_id = request.form.get('deck_id')
            if request.form.get('subdeck_id'):
                subdeck_id = request.form.get('subdeck_id')
                #DO STUFF



            #perform check here??!!?

            #paramzlied sql query

            card = Card(question = question,answer= answer,deck_id =request.form['deck_id'])
            db.session.add(card)
            db.session.commit()
    return render_template("create.html")

# #study entire deck, where there is a redirect to study each card
# @login_required
# @decks.route('/study-deck/<int:deck_id>')
# def study_deck(deck_id):

#     deck = Deck.query.filter_by(id=deck_id,user_id = current_user.id).first()
#     print('Revise deck')

#     return redirect(url_for('decks.decks_route'), permanent=True)

#study one card
@login_required
@decks.route('/study/<int:deck_id>',methods=['GET','POST'])
def study(deck_id):
    '''
    Allows the user to study new cards
    '''
    
    cards = Card.query.filter_by(deck_id=1).all()
    if request.method == 'POST':
        if request.form.get('quality'):
            question = request.form.get('quaity')

    

    return render_template("study.html")

#edit entire deck
@login_required
@decks.route('/edit-deck/<int:deck_id>',methods=['GET','POST'])
def edit_deck(deck_id):
    '''
    RECURSION FOR SUBDECKS???
    '''

    # new_subdeck= Deck(name='this is just a test', user_id=current_user.id, parent_id=18)
    # db.session.add(new_subdeck)
    # db.session.commit()
    try:
        current_deck = Deck.query.filter_by(id=deck_id,user_id =current_user.id).first()#.all()    parent_id=None,
    except Exception as e:
        flash('Error : {}'.format(e),category='danger')

    if current_deck is None:    
        flash('Deck id cannot be found',category='danger')
        return redirect(url_for('decks.decks_route'),code=301)
        
    #PREVENT SQL INJECTIONS HERE!!!
    if request.method== 'POST':
        print(request.form)
        if request.form.get('name'): #not checking if description is sent as its is optional
            name = request.form.get('name')
            description = request.form.get('description')
            current_deck.name = name
            current_deck.description = description
            db.session.commit()
            flash('Deck has been updated',category='success')
            #return redirect(url_for('decks.edit_deck',deck_id=deck_id),code=301)#301 is a permanent redirect

        elif request.form.get('delete_subdeck'):
            subdeck_id = request.form.get('delete_subdeck')

            deck_to_delete = Deck.query.get(subdeck_id)

            if deck_to_delete is None:
                flash('Deck with id {} not found'.format(deck_id), category='danger')
                return redirect(url_for('decks.edit_deck', deck_id=deck_id), code=301)

            db.session.delete(deck_to_delete)
            db.session.commit()
            flash('Subdeck has been deleted',category='success')
            return  redirect(url_for('decks.edit_deck',deck_id=deck_id),code=301)#301 is a permanent redirect


        elif request.form.get('add_subdeck'):
            if request.form.get('subdeck_name'):
                new_subdeck= Deck(name=request.form['subdeck_name'], user_id=current_user.id, parent_id=deck_id)
                db.session.add(new_subdeck)
                db.session.commit()
                flash('Subdeck has been added successfully',category='success')
                #return  redirect(url_for('decks.edit_deck',deck_id=deck_id),code=301)#301 is a permanent redirect

            else:
                flash('Please add a valid subdeck title, title is required',category='danger')
        else:
            flash('POST request has been recieved with no valid content',category='danger')
       # return redirect(url_for('decks.decks_route'),code=301)

    # put the infomraiton has a placeholder and check if there is a change, then check how to update deck info
    return render_template("edit_deck.html",deck=current_deck)




#edits individual cards
@login_required
@decks.route('/edit/<int:card_id>',methods=['GET','POST'])
def edit(card_id):
    '''
    Allows the user to edit existing cards
    '''
    #checks if the card is owned by user, if its not then this editing wont be allowed
    if not user_owned_card(card_id):
        return redirect(url_for('decks.decks_route'),code=301)

    # try:
    #     current_card = Card.query.filter_by(id=card_id).first()
    #     get_card_userid(card_id)
    # except Exception as e:
    #     flash('Error locating card: {}'.format(e),category='danger')

    try:
        current_card = Card.query.filter_by(id=card_id).first()
    except Exception as e:
        flash('Error : {}'.format(e),category='danger')

    if current_card is None:    
        flash('Card id cannot be found',category='danger')
    
    # #QUERY CARD OBJECT  AND PASS IT IN THEN UPDATE IT WITH CARD.QUESTION = QUEST.FORM['QUESITON]
    # print(request.form)
    # print(request)

    if request.method == 'POST':
        print('ENTERED 1')
        print(request.form.get('card-question'))
        print(request)
        if request.form.get('card-question') or request.form.get('card-answer'):
            current_card.question = request.form['card-question']
            current_card.answer = request.form['card-answer']
            db.session.commit()
            flash('Flashcard has been successfully updated',category='success')
            #REDIRECT BACK TO ITS PLACE
            return redirect(url_for('decks.browse'),code=301)

            #return redirect(request.referrer)
    current_card = Card.query.filter_by(id=card_id).first()
    return render_template("edit.html",card=current_card)



    #current_app.app_context().push()
# db.session.execute('DELETE * FROM Deck')
# db.session.commit()
#print(current_user)


# deck1 = Deck(name='Deck 1', user_id=)
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



#IN FLASHCARD

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


