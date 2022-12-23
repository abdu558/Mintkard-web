from flask import Blueprint, render_template
from . import db


decks = Blueprint('decks', __name__)

@decks.route('/decks')
def Decks():
    return render_template("decks.html")


@decks.route('/browse')
def Browse():
    return render_template("browse.html")


@decks.route('/study/<int:id>')
def Study(id):
    return render_template("study.html")

# @app.route("/user/<int:id>")
# def user_detail(id):
#MAKE EACH CARD HAVE A GET REQUEST WITH THE LINK CHANGING OF THE ID OF THGE CARD MAKING IT SHAREABELK???????????????????????!!!!!!!!
