from flask import Blueprint, render_template,request,url_for,redirect,flash,current_app,g
from . import db
from .models import User,Deck,Card
from flask_login import current_user,login_required
from datetime import datetime, timedelta 
from typing import List,Tuple
import requests
import uuid
import os
from werkzeug.utils import secure_filename
import hashlib
import random

decks = Blueprint('decks', __name__)

class FlashcardManager:
    def __init__(self,user,app):#user can be an int or an object, polymorphism
        self.app = app
        
        if isinstance(user, int):
            self.user= User.query.get(user)
        else:
            self.user = user


    '''returns a list of all the cards that the user owns'''
    def get_all_cards(self) -> List[Card]:
        cards = []
        for deck in self.user.decks:
            if deck.parent_id is None:#Starts from the top of the hierachy of a tree, where there is no parent node
                cards.extend(self.get_cards_from_deck(deck))
        return cards

    def get_cards_from_deck(self,deck: Deck) -> List[Card]:
        cards = deck.cards #gets the cards in the currrent deck, but cards in child_decks are not collected yet,they will be collected in the recursive call below
        for child_deck in deck.children_deck:# loops through all the children deck, and traverses each child deck 
            if (child_deck.children_deck is not None) and len(child_deck.cards)!= 0:#if the child deck, has no children deck than dont traverse them
                cards.extend(self.get_cards_from_deck(child_deck))
        return cards

    '''
    The two methods above work together to get all the cards in a tree, so get_all_cards (first method) will iterate throught each deck
    then it will pass one root deck to the get_cards_from_deck which traverses the tree by calling itself recursively on each child deck
    This means that the function will visit the nodes in a depth first search from the root node to the last decks in the bottom in the bottom of the hierarchy, 
    i.e. the leaf nodes without any child decks
    This is used in the browse cards route
    '''


    def get_all_decks(self):
        all_decks = []
        for root_deck in self.user.decks:
            if root_deck.parent_id is None:# this will only check parent decks
                all_decks.extend(self.get_all_decks_recursive(root_deck))
        return all_decks

    def get_all_decks_recursive(self,root_deck: Deck) -> List[Deck]:
        '''
        This is only called by get_all_decks
        It generates a list of all the subdeck of a root deck
        This is used to traverse all the root decks, such that every root deck is represented as a tree, so there are many trees.
        '''
        all_decks = [root_deck]
        for subdeck in root_deck.children_deck:
            all_decks.extend(self.get_all_decks_recursive(subdeck))# recursively calls itself
        return all_decks




    '''
    The following two function  is_card_due and get_flashcards_to_review are used in flashcard reviews and are used and work together 
    alongside the update_stats method in the card class
    '''
    #dates is a list of int/datetimes
    #reference: https://developer.nvidia.com/blog/merge-sort-explained-a-data-scientists-algorithm-guide/
    def merge_sort(self,dates):
        dates_len = len(dates)
        if dates_len <=1:
            return dates
            
        #divide and conquer
        middle = dates_len //2
        right = self.merge_sort(dates[middle:])
        left = self.merge_sort(dates[:middle])
        
        return self.merge_list(left,right)
        
    def merge_list(self,left,right):
        dates_list = []
        l=r=0#left and right
        while (r <len(right) and l<len(left)):
            if left[l].last_study < right[r].last_study:
                dates_list.append(left[l])
                l = l+1
            else:
                dates_list.append(right[r])
                r = r+1
        dates_list.extend(left[l:])
        dates_list.extend(right[r:])
        return dates_list



    def is_card_due(self,flashcard:Card) -> bool:
        '''
        Purpose of this method is to use the interval and last review date to determine the date that the card is due
        This method uses typing, to make sure that the input is a Card object and the output is a boolean value.
        This is only called by get_flashcards_to_review method
        '''
        if flashcard.is_new == True:
            return True
        try:
            review_interval = timedelta(days=flashcard.interval)#converts int to time using datetime module
            return (flashcard.last_study + review_interval <= datetime.now())
        except Exception as e:
            flash('ERROR: checking if card is due: {}'.format(e),category='danger')
            return True#True will let the card be reviewed, so that the error may get fixed



    def get_flashcards_to_review(self, deck_id_or_deck):
        '''
        This method is called to review decks, this will review all subdecks recusively
        This is method is called, when a user wants to review a deck/subdeck and it calls the is_card_Due method
        to check if the card is due to be reviewed.
        '''
        if isinstance(deck_id_or_deck, int):#Polymorphism
            deck= Deck.query.get(deck_id_or_deck)
        else:
            deck = deck_id_or_deck
        
        flashcards_to_review = []
        for flashcard in deck.cards:
            if self.is_card_due(flashcard):
                flashcards_to_review.append(flashcard)

        #searches for flashcards that are due, in subdecks recursively   
        for subdeck in deck.children_deck:
            flashcards_to_review.extend(self.get_flashcards_to_review(subdeck.id))

        '''
        There would be a list of all cards that are not new, as new cards do not have a interval or quality so new cards stay in the flashcards_to_review,
        whereas the cards that are not new, have been reviewed before, are moved onto a unsorted_list, which is merge sorted by due date, then combined back with the flashcards_to_review list'''
        unsorted_list = []
        for c in flashcards_to_review:
            if c.is_new == False:
                unsorted_list.append(c)
                flashcards_to_review.remove(c)
            
        sorted_list = self.merge_sort(unsorted_list)
        flashcards_to_review.extend(sorted_list)

        return flashcards_to_review




class FlashcardManagerStats(FlashcardManager):
    '''
    This class inherits from FlashcardManager and FlashcardManagerPublicStats inherits this Class

    .fetchone() will not get an error if there are no cards
    '''
    def __init__(self,user,app):
        super().__init__(user,app)
        self.flashcard_manager = FlashcardManager(user, app)#composition

    def good_cards_percent(self) -> float:
        '''
        avg quality- is the average quality of all cards
        good_cards - is the percentage of cards rated good, which is a 3 or 4 quality rating
        '''
        cards = self.flashcard_manager.get_all_cards()
        
        if len(cards) == 0:
            return 'No data'
        
        num_of_cards=0 #exclude the new cards
        good_quality = 0
        for card in cards:
            if card.is_new == True:
                continue
            elif card.quality > 2:
                good_quality += 1
                num_of_cards +=1
            elif card.quality <=2:
                num_of_cards +=1

        if num_of_cards == 0:
            return 'No data'

        try:
            good_cards = (good_quality/num_of_cards) *100 #turn into a percentage
        except Exception as e:
            print('good_cards_percent error when dividing',e)
            good_cards = 0
            return good_cards
            
        return good_cards


    def card_nums(self):
        data = len(self.flashcard_manager.get_all_cards())
        return data

    def deck_nums(self):
        '''
        returns the number of all cards including subdecks by countin the number of rows
        '''
        data = db.session.execute(f"SELECT COUNT(*) as deck_num FROM Deck WHERE user_id = {self.user.id};").fetchone()
        return data.deck_num


    def easiness_factor_avg(self):
        #Gets an average easiness factor of the user
        
        data = db.session.execute(f"SELECT AVG(easiness_factor) as easiness_avg FROM Card WHERE id IN (SELECT id FROM Deck WHERE user_id = {self.user.id});").fetchone()
        return data.easiness_avg


    def quality_avg(self):
        #gets an average quality of the user
        data = db.session.execute(f"SELECT AVG(quality) as quality_avg FROM Card WHERE id IN (SELECT id FROM Deck WHERE user_id = {self.user.id});").fetchone()
        return data.quality_avg

    def interval_avg(self):
        #gets an average interval
        data = db.session.execute(f"SELECT AVG(interval) as inter_avg FROM Card WHERE id IN (SELECT id FROM Deck WHERE user_id = {self.user.id});").fetchone()
        return data.inter_avg

    def get_all_data(self):
        'This function can be called to return all the data from all the above methods with one call rather than calling each method to generate the data for the stats page'
        success_rate = self.good_cards_percent()
        card_nums = self.card_nums()
        deck_nums = self.deck_nums()
        interval_avg = self.interval_avg()
        easiness_factor_avg = self.easiness_factor_avg()
        quality_avg = self.quality_avg()
        return success_rate,card_nums,deck_nums,interval_avg,easiness_factor_avg,quality_avg

class FlashcardManagerPublicStats(FlashcardManagerStats):
    '''
    This is the public stats class that gets stats averages from all users of the app, it inherits from flashcard manager stats
    Method overloading occurs as the methods from flashcardmanagerpublicstats and flashcardmanager stats are the same
    '''
    def __init__(self,app,user=None):
        super().__init__(app,user)    

    def good_cards_percent(self):
        '''
        avg quality- is the average quality of all cards
        good_cards - is the percentage of cards rated good, which is a 3 or 4 quality rating
        '''
        cards = Card.query.all()
        if len(cards) == 0:
            return 'No data'
        num_of_cards=0 #exclude the new cards
        good_quality = 0
        for card in cards:
            if card.is_new == True:
                continue
            elif card.quality > 2:
                good_quality += 1
                num_of_cards +=1
            elif card.quality <=2:
                num_of_cards +=1
        
        if num_of_cards == 0:
            return 'No data'
        
        good_cards = (good_quality/num_of_cards) *100 #turn into a percentage

        return good_cards

    #method overiding
    def card_nums(self):
        #gets the total amount of cards that exist
        result = db.session.execute("SELECT COUNT(*) as card_nums FROM Card;").fetchone()
        return result.card_nums

    def deck_nums(self):
        '''
        returns the number of all cards including subdecks
        '''
        data = db.session.execute("SELECT COUNT(*) as deck_num FROM Deck;").fetchone()
        return data.deck_num

    def easiness_factor_avg(self):
        #Generates an average of easiness factor of all users
        data = db.session.execute("SELECT AVG(easiness_factor) as easiness_avg FROM Card;").fetchone()
        return data.easiness_avg


    def quality_avg(self):
        #Generates an average quality using data from all the users
        data = db.session.execute("SELECT AVG(quality) as quality_avg FROM Card;").fetchone()
        return data.quality_avg

    def interval_avg(self):
        #Generates an average interval from all the users
        data = db.session.execute("SELECT AVG(interval) as inter_avg FROM Card;").fetchone()
        return data.inter_avg

#Globally initlize flashcard manager, to be accessed in all routes, g. is global.
#its a complex user-defined oop model, will only be inilized with the user sending a request,

@decks.before_request
@login_required
def before_request():
    '''
    These clases are globally initlised at runtime, when the user sends the first request.
    '''
    try:
        g.fmanager = FlashcardManager(user=current_user.id, app=current_app)
        g.fmanagerstats = FlashcardManagerStats(user=current_user.id, app=current_app)
        g.fmanagerstats_public = FlashcardManagerPublicStats(user=None,app=current_app)#there is no user as it gets the apps average data

    except Exception as e:
        flash('Error inilizing flashcard manager: {}'.format(e),category='danger')
        

def user_owned_card(card_id):
    '''Returns true if the user does own the flashcard, false if the user does not, preventing unauthorised access of cards, if it the id is changed
    ON means what two tables should there should be a match in'''
    result = db.session.execute("""
        SELECT deck.user_id
        FROM card card
        INNER JOIN deck deck ON card.deck_id = deck.id
        WHERE card.id = {}
    """.format(card_id))
    try:
        if result.fetchone()[0] == current_user.id:
            return True
        return False
    except Exception:
        flash('Error validating card owner',category='danger')
        redirect(url_for('decks.browse'))
    
def deck_id_dict(decks):
    '''A dictionary of all decks,subdecks and their id, used to show the deck in the frontend'''
    deck_dict ={}
    for d in decks:
        deck_dict[d.id] = d.name
    return deck_dict


#Image support code is from flask documentation,reference: https://flask.palletsprojects.com/en/2.2.x/patterns/fileuploads/
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ['png', 'jpg', 'jpeg', 'gif','webp']

#files is going to be request.files.get('image')
#generate a unique file name and save it
#return the file name
#update the database

def upload_image(image):
    if image.filename=='':
        flash('No image upload detected',category='info')
        return False
    if image and allowed_file(image.filename):
        filename=image.filename
        if not os.path.exists('mintkard/static/user_images'):
            # Create the directory, if it does not exist
            os.makedirs('mintkard/static/user_images')

        filename = str(hashlib.md5(image.read()).hexdigest()) + '.' + filename.rsplit('.', 1)[1].lower()
        image.seek(0)#stops the image file from corrupting, by setting its default position in the file stream

        #saves the image in the user images folder, its in the static file so that it can be reterived and viewed in the website, as flask only renders files in the static file
        image.save(os.path.join('mintkard/static/user_images',filename))
        return filename
    return False

@decks.route('/home',methods=['GET','POST'])
@decks.route('/',methods=['GET','POST'])
@login_required
def decks_route():
    '''
    This is the main homepage for the decks page, where all decks(set of cards) are shown and their subdecksThey will have the option to study a deck, edit a deckThe name is deck_route, because if its called decks it would cause an error as its the same name as the registered blueprint
    by default, its get so if a post request is going to be recived in the route, it must be specified a post, and also a get to get the page request
    This can be visited with /decks/ or /decks/home, they will both visit this page
    login_required means that the user must be logged in, if the user isnt then they are redirected to login page, where they can also choose to register
    the login page is the redirect location as it is specified as the redirect in the __init__ file where the route auth.login is configured.
    root deck is a deck without a parent deck, just like a root is the start node of a tree data structure
    '''
    root_decks = Deck.query.filter_by(parent_id=None,user_id =current_user.id).all()

    #if the user clicks on add new deck button, then a deck with a random default image is selected and the default name of untitled deck is given and it is commited to the database
    #they can choose to edit the deck and change the image and name, a random image is slected so that each deck has a lower chance of having the same default image
    if request.form.get('add_deck'):
        image_num = random.randint(0,26)
        new_deck = Deck(name='Untitled Deck',image_hash = str(image_num) + '.jpg',user_id=current_user.id)
        db.session.add(new_deck)
        db.session.commit()
        return redirect(url_for('decks.edit_deck',deck_id=new_deck.id),code=301)

    #delete deck button will delete the deck from the database
    if request.form.get('delete_deck'):
        deck_id = request.form.get('delete_deck')
        try:
            deck_id = request.form['delete_deck']
            deck_to_delete = Deck.query.get(deck_id)

            #if a user inspect elements the deck and changes the ID, this will check if the selected deck is owned by the user
            if deck_to_delete.user_id != current_user.id:
                flash("WARNING: deck has not been deleted, do not attempt and delete decks you don't own",category='danger')
                return redirect(url_for('decks.decks_route'),code=301)

        except Exception as e:
            flash('Error locating deck: {}'.format(e),category='danger') 

        #delete the subdecks of the deck that is being deleted
        decks_to_delete = g.fmanager.get_all_decks_recursive(deck_to_delete)
        for delete_deck in decks_to_delete:
            db.session.delete(delete_deck)

        db.session.commit()

        #get all the decks that are the root of the tree in the decks hierarchy, for the main webpage
        root_decks = Deck.query.filter_by(parent_id=None,user_id=current_user.id).all()
        return render_template("decks.html",root_decks= root_decks)

    return render_template("decks.html",root_decks= root_decks)

@login_required
@decks.route('/stats', methods=['GET', 'POST'])
def stats():
    '''
    Generates the statistics for the stats page using the classes of flashcardmanager stats and flashcardmanagerpublicstats
    '''
    try:
        user_data = g.fmanagerstats.get_all_data()
        public_data = g.fmanagerstats_public.get_all_data() #inherited method
        user_data = [round(i,2) if i is not None else None for i in user_data]
        public_data = [round(i,2) if i is not None else None for i in public_data]
        info = ['Success rate','Number of cards','Number of decks and subdecks','Average interval','Average easiness factor','Average quality']
        data = tuple(zip(info,user_data,public_data))

    except Exception as e:
        flash('Error loading data, try adding a deck,cards and reviewing them first: {}'.format(e),category='danger')
        return(redirect(url_for('decks.decks_route')))

    return render_template("stats.html",data=data)


@login_required
@decks.route('/browse',methods=['GET','POST'])
def browse():
    '''
    Browse page which allows users to search phrases or words in cards, filter the results. It also allows users to delete and edit all the cards.
    '''
    deck_dict = deck_id_dict(g.fmanager.user.decks)
    #keeps the selected filter the same after a post request,
    if request.form.get('filter') == 'All':
        selected_id = request.form.get('filter')
    else:
        selected_id = int(request.form.get('filter')) if request.form.get('filter') is not None else None
    
    if request.form.get('delete_card'):
        card_id = request.form['delete_card']
        try:

            card_to_delete = Card.query.get(card_id)
            #Incase a user inspect elements the card and changes the ID, this will check the card he is deleting has the correct userid
            if card_to_delete.deck.user_id != current_user.id:
                flash("WARNING: card has not been deleted, do not attempt and delete card you don't own",category='danger')
                return redirect(url_for('decks.browse'),code=301)
            db.session.delete(card_to_delete)
            db.session.commit()
        except Exception as e:
            flash('Error locating card: {}'.format(e),category='danger')

    #if a user enters a search input
    elif request.args.get('search'):
        search_term = request.args.get('search')
        try:
            cards = db.session.execute(f"SELECT card.id FROM card INNER JOIN deck ON card.deck_id = deck.id WHERE deck.user_id = {current_user.id} AND (card.question LIKE '%{search_term}%' OR card.answer LIKE '%{search_term}%');").all()

            #loop replaced all the card ids in the card list with card objects
            for i in range(len(cards)):
                cards[i] = Card.query.filter_by(id=cards[i][0]).first()

            
            if request.form.get('filter'): #if a user selects a filter and searches, then the search results will only show up in the selected filter
                deck_id = request.form['filter']
                deck_filter = Deck.query.get(deck_id)
                cards_filtered = g.fmanager.get_cards_from_deck(deck_filter)
                
                for i in range(len(cards)):
                    #in the search, if the results are not in the filter and there is a filter applied then remove those cards from the search results
                    if cards[i] not in cards_filtered:
                        cards.remove(cards[i])
                

                        
                # for i in range(len(cards)):
                #     if cards[i] in 
        except Exception as e:
            flash('Error searching for cards: {}'.format(e),category='danger')
        
        
    #If there is a deck filter, that is not ALL or None then get all the card from that deck and its subdecks
    elif (request.method == 'POST') and (request.form.get('filter') not in (None, 'All')):
        deck_id = request.form['filter']
        try:
            deck_filter = Deck.query.get(deck_id)
            cards = g.fmanager.get_cards_from_deck(deck_filter)
        except Exception as e:
            flash('Error locating deck: {}'.format(e),category='danger')

    else:
        try:
            cards = g.fmanager.get_all_cards()
        except Exception as e:
            flash('Error locating decks: {}'.format(e),category='danger')


    #Incase of any possible issues, that results in cards not being generated, the full cards list is given
    try:
        cards
    except (NameError,UnboundLocalError):
        cards = g.fmanager.get_all_cards()

    #generate the decks used in the filter dropdown
    try:
        root_deck = [deck for deck in g.fmanager.user.decks if deck.parent_id == None]
    except Exception as e:
        flash('Error locating decks: {}'.format(e),category='danger')

    return render_template("browse.html",cards = cards,decks=root_deck,selected_id=selected_id,all_decks = g.fmanager.user.decks,deck_dict=deck_dict)


@login_required
@decks.route('/create',methods=['POST','GET'])
def create():
    '''
    Allow the users to create cards, and assign them to a any deck/subdeck
    '''
    
    if request.method == 'POST':
        if request.form.get('question') and request.form.get('deck'):
            try:
                question = request.form.get('question')
                answer = request.form.get('answer')
                deck_id = request.form.get('deck')

                if request.files.get('image'):
                    image_hash = upload_image(request.files['image'])
                    if image_hash != False:
                        card = Card(question = question,answer= answer,deck_id =deck_id,image_hash=image_hash)
                    else:
                        flash('Image has not been saved, please use a correct image format of png, jpg, jpeg, gif,webp',category='danger')
                        card = Card(question = question,answer= answer,deck_id =deck_id)
                else:
                    card = Card(question = question,answer= answer,deck_id =deck_id)    
                db.session.add(card)
                db.session.commit()
                flash('Card successfully added',category='success')
            except Exception as e:
                flash('Error adding card, report to the developer or try again later: {}'.format(e),category='danger')
        else:
            flash('Error: Please select a valid deck or add a question',category='danger')

    

    try:
        root_deck = [deck for deck in g.fmanager.user.decks if deck.parent_id == None]# used in the filter dropdown option 
    except:
        flash('Error locating decks: {}'.format(e),category='danger')
    return render_template("create.html",decks=root_deck)

#study one card
@login_required
@decks.route('/study/<int:deck_id>',methods=['GET','POST'])
def study(deck_id):
    '''
    Allows the user to study cards that are new or are due
    '''
    flashcards = g.fmanager.get_flashcards_to_review(deck_id)

    if request.method == 'POST':
        quality = int(request.form.get('quality'))
        if len(flashcards) == 0: #if the user refreshes and sends another post request
            return redirect(url_for('decks.study', deck_id=deck_id), code=301)
        flashcards[0].update_stats(quality)

        db.session.commit()

        flashcards.pop(0)#Remove the first item from the stack

    return render_template("study.html",flashcard = flashcards[0] if flashcards else None)

@login_required
@decks.route('/edit-deck/<int:deck_id>',methods=['GET','POST'])
def edit_deck(deck_id):
    '''
    Edit deck name,deck image,descritption and subdecks
    '''
    try:
        #Get the current deck as an object
        current_deck = Deck.query.filter_by(id=deck_id,user_id =current_user.id).first()
    except Exception as e:
        flash('Error : {}'.format(e),category='danger')

    if current_deck is None:
        flash('Deck id cannot be found',category='danger')
        return redirect(url_for('decks.decks_route'),code=301)#301 is a permanent redirect
        
    if request.method== 'POST':
        #if the name or the description is changed, then update them in the database
        if request.form.get('name') or request.form.get('description'):
            name = request.form.get('name')
            description = request.form.get('description')
            current_deck.name = name
            current_deck.description = description
            db.session.commit()
            flash('Deck has been updated',category='success')

        if request.files.get('image'):
            image_hash = upload_image(request.files['image'])
            if image_hash not in(None,False,current_deck.image_hash): #if there is a new image hash that is valid then update the deck in the database with the new image
                current_deck.image_hash = image_hash
                db.session.commit()
            else:
                print('Failed to upload image')
            
        elif request.form.get('delete_subdeck'):
            #get the id of the subdeck, turn it into a object and delete it
            subdeck_id = request.form.get('delete_subdeck')
            deck_to_delete = Deck.query.get(subdeck_id)

            if deck_to_delete is None:
                flash('Deck with id {} not found'.format(subdeck_id), category='danger')
                return redirect(url_for('decks.edit_deck', deck_id=deck_id), code=301)

            #delete the subdecks of the deleted deck
            decks_to_delete = g.fmanager.get_all_decks_recursive(deck_to_delete)

            for delete_deck in decks_to_delete:
                #delete all cards in the deck
                for c in delete_deck.cards:
                    db.session.delete(c)
                db.session.delete(delete_deck)

            db.session.commit()

            flash('Subdeck has been deleted',category='success')
            return  redirect(url_for('decks.edit_deck',deck_id=deck_id),code=301)#301 is a permanent redirect


        elif request.form.get('add_subdeck'):
            #if a new subdeck is added, update the database and insert a new deck with the parent being the current deck
            if request.form.get('subdeck_name'):
                new_subdeck= Deck(name=request.form['subdeck_name'], user_id=current_user.id, parent_id=deck_id)
                db.session.add(new_subdeck)
                db.session.commit()
                flash('Subdeck has been added successfully',category='success')
            else:
                flash('Please add a valid subdeck title, title is required',category='danger')

    return render_template("edit_deck.html",deck=current_deck)

@login_required
@decks.route('/edit/<int:card_id>',methods=['GET','POST'])
def edit(card_id):
    '''
    Allows the user to edit existing,individual cards
    '''
    #checks if the card is user-owned, if its not then access will be denied
    if not user_owned_card(card_id):
        return redirect(url_for('decks.decks_route'),code=301)

    #Gets all the root decks so it can be displayed in the decks dropdown menu
    try:
        decks = [deck for deck in g.fmanager.user.decks if deck.parent_id == None]# used in the filter dropdown option 
    except Exception as e:
        flash('Error locating decks: {}'.format(e),category='danger')

    try:
        #gets the card object using the card id
        current_card = Card.query.filter_by(id=card_id).first()
    except Exception as e:
        flash('Error : {}'.format(e),category='danger')

    if current_card is None:
        #if current_card does not exist or has an error
        flash('Card id cannot be found',category='danger')
    
    if request.method == 'POST':

        if request.form.get('deck'):
            #if the deck location has changed, update it in the database
            if request.form.get('deck') not in ('same',None,current_card.deck_id):
                deck_id = request.form.get('deck')
                current_card.deck_id = deck_id
                db.session.commit()

        #if any of the fields are not empty, update the card
        if request.form.get('card-question') or request.form.get('card-answer') or request.files.get('image'):
            current_card.question = request.form['card-question']
            current_card.answer = request.form['card-answer']

            #images upload
            if request.files.get('image'):
                image_hash = upload_image(request.files['image'])
                
                #if the image did not get uploaded correctly, or is the same dont append the image hash attribute in the database
                if image_hash not in(None,False,current_card.image_hash):
                    current_card.image_hash = image_hash
                else:
                    print('Failed to upload image')

            db.session.commit()
            
            flash('Flashcard has been successfully updated',category='success')
            return redirect(url_for('decks.browse'),code=301)
        else:
            flash('Please fill out the form',category='danger')
            return redirect(url_for('decks.edit',card_id=card_id),code=301)

    current_card = Card.query.filter_by(id=card_id).first()
    return render_template("edit.html",card=current_card,decks=decks)



@decks.route('/help') 
def help():
    '''
    Help guide which also has a help guide
    '''
    return render_template("help.html")