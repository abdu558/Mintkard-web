from flask import Blueprint, render_template,request
#Boilerplate code that registers auth file with init file
auth = Blueprint('auth', __name__)

#ADD SOME CEHCKING SUCH AS LENGTHS AND SUCH


#methods is get by default, adding post will allow the submission of login info without it showing up in link
@auth.route('/login',methods=['GET','POST'])
def login():
    #uses the request module to give the data that was send as part of a form
    #This will check data that is recieved via a POST request only as that's how the login data is entered with
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')


    return render_template("login.html")


@auth.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password1')
        confirm_password = request.form.get('password2')


    return render_template("register.html")


@auth.route('/logout')
def logout():
    return render_template("logout.html")
