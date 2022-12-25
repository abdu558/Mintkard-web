from flask import Blueprint, render_template,request,url_for,redirect,flash
from . import db
from .models import User,Deck,Card
from flask_login import current_user

decks = Blueprint('decks', __name__)


'''
TO-DO
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
def decks_route():
    '''
    This is the main homepage for the decks page, where all decks(set of cards) are shown and their subdecks
    They will have the option to study a deck, edit a deck, CHECK LATER HOW TO REDIRECT EDIT DECKS TO THE RIGHT DECK.
    The name is deck_route, because if its called decks it would cause an error as its the same name as the registered blueprint
    '''
    return render_template("decks.html",curernt_user=current_user)


@decks.route('/browse')
def browse():
    return render_template("browse.html")

@decks.route('/create')
def create():
    '''
    Allows the user to create a new card
    '''
    return render_template("create.html")

@decks.route('/study/<int:id>')
def study(id):
    '''
    Allows the user to study new cards
    '''
    return render_template("study.html")

@decks.route('/edit/<int:id>')
def edit(id):
    '''
    Allows the user to edit existing cards
    '''
    return render_template("edit.html")

# @app.route("/user/<int:id>")
# def user_detail(id):
#MAKE EACH CARD HAVE A GET REQUEST WITH THE LINK CHANGING OF THE ID OF THGE CARD MAKING IT SHAREABELK???????????????????????!!!!!!!!
