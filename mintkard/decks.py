from flask import Blueprint, render_template

decks = Blueprint('decks', __name__)

@decks.route('/')
def home():
    return render_template("home.html")


@decks.route('/Browse')
def browse():
    return render_template("home.html")


@decks.route('/Study')
def Study():
    return render_template("home.html")
