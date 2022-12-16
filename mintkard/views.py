from flask import Blueprint, render_template

views = Blueprint('views', __name__)

#This is the home page, where / and /home will both lead to the home page
@views.route('/')
@views.route('/home')
def Home():
    return render_template("home.html")



