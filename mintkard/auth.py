from flask import Blueprint, render_template,request

auth = Blueprint('auth', __name__)

@auth.route('/login',methods=['GET','POST'])
def login():
    
    return render_template("home.html")


@auth.route('/register')
def register():
    return render_template("home.html")


@auth.route('/logout')
def logout():
    return render_template("home.html")
