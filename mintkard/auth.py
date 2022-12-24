from flask import Blueprint, render_template,request,url_for,redirect,flash
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from flask_login import login_user,login_required,logout_user,current_user
from . import db #Import the User class from the models file
#CHECK IF ABOVE ONE IS CORRECT

#flask setup code that registers auth file with init file/app
auth = Blueprint('auth', __name__)




def check_email(email):
    '''
    Check if the email is valid
    They are if statemnts as they are all independent of each other
    if true return '' instead of None as it will be easier to check for errors in the error variable
    '''
    error = False
    # if len(email) < 6:
    #     error = "Email must be at least 5 characters"
    if "@" not in email:
        error = "Email must be valid"
    elif "." not in email:
        error= "Email must have a ."
    elif " " in email:
        error = "Email must not contain spaces"

    #If there is an error, return the error, if not return None and True which would let the user continue/add to the database
    if error:
        return False, error
    else:
        return True, ''

def check_username(username):
    '''
    Username validation, to check length and if it contains spaces
        if true return '' instead of None as it will be easier to check for errors in the error variable

    '''
    error = False
    if len(username) < 4 :
        error = "Username must be at least 4 characters"
    elif " " in username:
        error = "Username must not contain spaces"


    #If there is an error, return the error, if not return None and True which would let the user continue/add to the database
    if error:
        return False, error
    else:
        return True, ''

def check_password(password,confirm_password):
    '''
    Password validation, to check length and if it contains spaces
    if true return '' instead of None as it will be easier to check for errors in the error variable

    '''
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
        return True, ''


#methods is get by default, adding post will allow the submission of login info without it showing up in link
@auth.route('/login',methods=['GET','POST'])
def login():
    '''
    This function will get the data from the template login.html and would get the data by the name in the html form, it will check if the fields are filled out
    uses the request module to give the data that was send as part of a form
    This will check data that is recieved via a POST request only as that's how the login data is entered with
    '''
    # #uses the request module to give the data that was send as part of a form
    # #This will check data that is recieved via a POST request only as that's how the login data is entered with
    if request.method == 'POST':
        #Check if the email and password are sent, No need to check with the functions
        if request.form.get('email') and request.form.get('password'):
            email = request.form.get('email')
            password = request.form.get('password')
            #If they are in the database, log them in
            #If they are not in the database, return an error to create an account

            #if email=='bob@gmail.com' and password=='bob':

            if email == User.query.filter_by(email=email).first().email and check_password_hash(User.query.filter_by(email=email).first().password,password)[0]:#Why 0
                flash('You were successfully logged in')
                login_user(user)
                return redirect(url_for('decks.Decks'))
            else:
                flash('Email or password is incorrect',category='danger')

        else:
            flash('Please fill out all fields',category='danger')

    return render_template("login.html")


@auth.route('/register',methods=['GET','POST'])
def register():
    '''
    This function will get the data from the template register.html and would get the data by the name in the html form, it will check if the fields are filled out
    It will also will check if the email,username and passwords are valid, if not they would be redirected to the register page with an error
    If they are valid, it will check if the email and username are already in the database, if they are, it will return an error
    If they are not in the database, it will add them to the database and redirect to the decks page

    
    '''
    if request.method == 'POST':#add an else statemnet to this

        #ASSIGN THE username and email and password to variables in a try and except and the except would be a flash message, remove the return redirect
        # try:
        #     username = request.form.get('username')
        #     email = request.form.get('email')
        #     password = request.form.get('password1')
        #     confirm_password = request.form.get('password2')
        # except:
        #     flash('Please fill out all fields',category='danger')
        #     return redirect(url_for('auth.register'))

        #Checks if all fields are filled out
        if request.form.get('username') and request.form.get('email') and request.form.get('password1') and request.form.get('password2'):#DOES THIS WORK TO CHECK IF SOMETHING IS IN OR DOES IT WORK FOR ONLY TRUE VALUES?
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password1')
            confirm_password = request.form.get('password2')
            #Checks if the email,username and passwords are valid, if not they would be redirected to the register page with an error
            print(check_email(email))
            print(check_username(username))
            print(check_password(password,confirm_password))
            if check_email(email)[0] and check_username(username)[0] and check_password(password,confirm_password)[0]:
                #Check if the email is already in the database
                #Check if the username is already in the database
                #If both are not in the database, add them to the database
                #If either are in the database, return an error
                if email == 'bob@gmail.com':
                    flash('Email already in use',category='danger')
                    return redirect(url_for('auth.register'))
                if username == 'bob':
                    flash('Username already in use',category='danger')
                    return redirect(url_for('auth.register'))

                #ADD TO DATABASE and come up with an id
                new_user = User(username=username,email=email,password=generate_password_hash(password,method='sha256'))
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user,remember=True)#Changes remember me to the option of ticked
                flash('Account successfully created',category='success')
                return redirect(url_for('decks.Decks'))
            else:
                try:
                    #If the mutltiple functions return error message seperate them with a comma, if they are empty do not add a comma 
                    error = check_email(email)[1] + check_username(username)[1] + check_password(password,confirm_password)[1]
                    flash(error,category='danger')
                    return render_template("register.html",error=error)
                except:
                    flash('ERROR PLEASE TRY AGAIN',category='danger')

                return render_template("register.html")

        flash('Please fill out all fields',category='danger')
        
    return render_template("register.html")


@auth.route('/logout')
def Logout():
    return render_template("logout.html")
