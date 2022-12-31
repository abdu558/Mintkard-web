from flask import  Flask, Blueprint, render_template
from flask_login import current_user

views = Blueprint('views', __name__)

#This is the home page, where / and /home will both lead to the home page
@views.route('/')
@views.route('/home')
def home():
    return render_template("home.html",current_user=current_user)

