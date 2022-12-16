from flask import Blueprint, render_template,request,url_for,redirect,flash
#flask setup code that registers auth file with init file/app
auth = Blueprint('auth', __name__)

def check_email(email):
    #Check if the email is valid
    #They are if statemnts as they are all independent of each other
    error = False
    if len(email) < 6 :
        error = "Email must be at least 5 characters"
    elif "@" not in email:
        error = "Email must be valid"
    elif "." not in email:
       error= "Email must have a ."
    elif " " in email:
        error = "Email must not contain spaces"

    #If there is an error, return the error, if not return None and True which would let the user continue/add to the database
    if error:
        return False, error
    else:
        return True, None

def check_username(username):
    #Username validation, to check length and if it contains spaces
    error = False
    if len(username) < 4 :
        error = "Username must be at least 4 characters"
    elif " " in username:
        error = "Username must not contain spaces"


    #If there is an error, return the error, if not return None and True which would let the user continue/add to the database
    if error:
        return False, error
    else:
        return True

def check_password(password,confirm_password):
    error = False
    #Check if the password is valid
    if len(password) < 5 :
        error = "Password must be at least 5 characters"
    #Check if the password contains spaces
    elif " " in password:
        error = "Password must not contain spaces"
    #Check if the password matches the confirm password
    elif password != confirm_password:
        error = "Passwords do not match"
    
    #If there is an error, return the error, if not, return None and True which would let the user continue/add to the database or login
    if error:
        return False, error
    else:
        return True


#methods is get by default, adding post will allow the submission of login info without it showing up in link
@auth.route('/login',methods=['GET','POST'])
def Login():
    # #uses the request module to give the data that was send as part of a form
    # #This will check data that is recieved via a POST request only as that's how the login data is entered with
    if request.method == 'POST':
        #Check if the email and password are sent, No need to check with the functions
        if request.form.get('email') and request.form.get('password'):
            email = request.form.get('email')
            password = request.form.get('password')
            #If they are in the database, log them in
            #If they are not in the database, return an error to create an account
            if email=='bob@gmail.com' and password=='bob':
                flash('You were successfully logged in')
                return redirect(url_for('decks.Decks'))
            else:
                flash('Email or password is incorrect',category='error')

        else:
            flash('Please fill out all fields',category='error')

    return render_template("login.html")


@auth.route('/register',methods=['GET','POST'])
def Register():
    if request.method == 'POST':#add an else statemnet to this
        #Checks if all fields are filled out
        if request.form.get('username') and request.form.get('email') and request.form.get('password1') and request.form.get('password2'):#DOES THIS WORK TO CHECK IF SOMETHING IS IN OR DOES IT WORK FOR ONLY TRUE VALUES?
            #Checks if the email,username and passwords are valid, if not they would be redirected to the register page with an error
            if check_email(request.form.get('email')) and check_username(request.form.get('username')) and check_password(request.form.get('password1'),request.form.get('password2')):
                username = request.form.get('username')
                email = request.form.get('email')
                password = request.form.get('password1')
                confirm_password = request.form.get('password2')

                #Check if the email is already in the database
                #Check if the username is already in the database
                #If both are not in the database, add them to the database
                #If either are in the database, return an error
                if email == 'bob@gmail.com':
                    flash('Email already in use',category='error')
                    return redirect(url_for('auth.register'))
                if username == 'bob':
                    flash('Username already in use',category='error')
                    return redirect(url_for('auth.register'))

                #ADD TO DATABASE

                flash('Account successfully created')
                return redirect(url_for('decks.Decks'))
            else:
                error = check_email(request.form.get('email'))[1] + check_username(request.form.get('username'))[1] + check_password(request.form.get('password1'),request.form.get('password2'))[1]
                return render_template("register.html",error=error) #GET ERROR FROM THE CHECK FUNCTIONS
        flash('Please fill out all fields',category='error')
        
    return render_template("register.html")


@auth.route('/logout')
def Logout():
    return render_template("logout.html")
