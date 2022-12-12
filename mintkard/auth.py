from flask import Blueprint, render_template,request

auth = Blueprint('auth', __name__)

#methods is get by default, adding post will allow the submission of login info without it showing up in link
@auth.route('/login',methods=['GET','POST'])
def login():
    #uses the request module to give the data that was send as part of a form
    data = request.form
    print(data)
    return render_template("login.html")


@auth.route('/register')
def register():
    return render_template("register.html")


@auth.route('/logout',methods=['GET','POST'])
def logout():
    return render_template("logout.html")
