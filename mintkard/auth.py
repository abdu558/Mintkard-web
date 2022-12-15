from flask import Blueprint, render_template,request,url_for,redirect,flash
#flask setup code that registers auth file with init file/app
auth = Blueprint('auth', __name__)

def check_email(email):
    #Check if the email is valid
    if len(email) < 4 :
        return render_template("register.html",error="Email must be at least 4 characters")
    elif "@" not in email:
        return render_template("register.html",error="Email must be valid")
    elif "." not in email:
        return render_template("register.html",error="Email must contain a .")
    elif " " in email:
        return render_template("register.html",error="Email must not contain spaces")
    return True

def check_username(username):
    #Check if the username is valid
    if len(username) < 4 :
        return render_template("register.html",error="Username must be at least 4 characters")
    elif " " in username:
        return render_template("register.html",error="Username must not contain spaces")
    return True

def check_password(password,confirm_password):
    #Check if the password is valid
    if len(password) < 6 :
        return render_template("register.html",error="Password must be at least 6 characters")
    elif " " in password:
        return render_template("register.html",error="Password must not contain spaces")
    elif password != confirm_password:
        return render_template("register.html",error="Passwords must match")
    return True


#methods is get by default, adding post will allow the submission of login info without it showing up in link
@auth.route('/login',methods=['GET','POST'])
def login():
    # #uses the request module to give the data that was send as part of a form
    # #This will check data that is recieved via a POST request only as that's how the login data is entered with
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

    
    #Check if all fields are filled out
    if username and email and password and confirm_password:
        #Check if the email,username and passwords are valid, if not they would be redirected to the register page with an error
        if check_email(email) and checek_username(username) and check_password(password,confirm_password):
            #Check if the email is already in the database
            #Check if the username is already in the database
            #If both are not in the database, add them to the database
            #If either are in the database, return an error
            return redirect(url_for('auth.login'))
            


        else:
            flash('You were successfully logged in')
            return redirect(url_for('decks.decks'))
    else:
        return render_template("register.html",error="Please fill out all fields")
        #Check if the email is already in the database
        #Check if the username is already in the database
        #If both are not in the database, add them to the database
        #If either are in the database, return an error


    return render_template("register.html")


@auth.route('/logout')
def logout():
    return render_template("logout.html")
