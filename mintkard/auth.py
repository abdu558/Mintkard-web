from flask import Blueprint, render_template,request,url_for,redirect,flash
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from flask_login import login_user,login_required,logout_user,current_user
from . import db #Relative import of the database connection
import re #regular expressions library

#flask setup code that registers this auth file with init file/app
auth = Blueprint('auth', __name__)


def check_email(email):
    '''
    [a-zA-Z0-9_.+-] means any alphabet or number and the 4 symbols which are allowed in an email
    the + sumbol means that the length of the square brackets must be 1 character or longer, so empty spaces get rejected
    the \ will let the period be trated as a period rather than special regex character
    the +$ will mean it represents the endof the domain name of the email
    Only english emails work
    '''
    pattern = r"^[a-zA-Z0-9-`{}_~'*+/=?!#$%&^]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    match = bool(re.fullmatch(pattern,email))
    if match == True:
        return match,''
    else:
        return match,'Please enter a valid email,'
 
def valid_char(user_input):
    '''
    Returns True if it is using a valid set of characters
    '''
    # Checks for invalid characters, such as semicolons to make it more difficult for SQLinjections
    if re.match(r"^[a-zA-Z0-9-\.@`{}_~'+/=?!#$%&^]+$", user_input):
        return True
    return False


def check_username(username):
    '''
    Username validation, to check length and if it contains spaces
    if true return '' instead of None as it will be easier to check for errors in the error variable
    '''
    error = False
    if len(username) < 1:
        error = "Username must be at least 1 characters"
    elif " " in username:
        error = "Username must not contain spaces"
    elif not valid_char(username):
        error = "Invalid characters used, please only use characters,numbers and -\.@`{}_~'+/=?!#$%&^"

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
    if len(password) < 4 :
        error = "Password must be at least 4 characters"
    #Check if the password contains spaces
    elif " " in password:
        error = "Password must not contain spaces"
    #Check if the password matches the confirm password
    elif password != confirm_password:
        error = "Passwords do not match"
    #Check if password does not have a valid character
    elif not valid_char(password):
        error = "Invalid characters used, please only use characters,numbers and -\.@`{}_~'+/=?!#$%&^"    

    #If there is an error, return the error, if not, return '' and True which would let the account register or login
    if error:
        return False, error
    else:
        return True, ''

def check_email_exists(email):
    '''
    Checks if the email is already in the database
    Returns true if an email match is found, else it would return false
    '''

    if User.query.filter_by(email=email).first():
        return True
    return False

def check_username_exists(username):
    '''
    Checks if the username is already in the database
    Returns true if a username match is found, else it would return false
    '''
    if User.query.filter_by(username=username).first():
        return True
    return False
    

#methods is GET by default, To add adding post will allow the submission of login info without it showing up in link
@auth.route('/login',methods=['GET','POST'])
def login():
    '''
    In the above auth.route, auth is due to the name declared in the blueprint, the methods are specified in this route due to it being GET by default and post is added and needed, 
    as POST requests are required for senseitive login info being sent which shouldnt be shown in the link.

    This function will get the data from the template login.html and would get the data
    using the request module to get the data from the form to this route in the backend.
    '''

    #This will check data that is recieved via a POST request only as that's how the login data is entered with, and to avoid the access of the page which occurs as a GET request
    if request.method == 'POST':
        #Check if the email and password are recieved and they are not None
        if request.form.get('email') and request.form.get('password'):
            email = request.form.get('email') #assign them locally
            password = request.form.get('password')

            #If they are in the database,and the password is correct log them in
            #If they are in the database, and the password is wrong, return an error
            #If they are not in the database, return an error account doesnt exist

            if not check_email_exists(email):
                flash('Email is not registered, Register instead?',category = 'danger')
                return redirect(url_for('auth.register'))
            
            #checks if the users password does not match, if it does not match the one registreerd with the email in the database, then an error occurs
            if not(check_password_hash(User.query.filter_by(email=email).first().password,password)):#Why 0
                flash('Email or password is incorrect',category='danger')
                return redirect(url_for('auth.login'))

            try:
                #Gets the user objects and passes it to Flasklogin to complete the login
                user = User.query.filter_by(email=email).first()
                login_user(user)
            except Exception as e:
                flash('Error logging in user: {}'.format(e),category='danger')
                return redirect(url_for('auth.login'))

            flash('You were successfully logged in',category='success')
            #if successful, then redirect them to decks home
            return redirect(url_for('decks.decks_route'))
        else:
            flash('Please fill out all fields',category='danger')
            return redirect(url_for('auth.login'))
    return render_template("login.html")


@auth.route('/register',methods=['GET','POST'])
def register():
    '''
    This function will get the data from the frontend register page and the request module is used to recieve the data
    It will also will check if the email,username and passwords are valid,with the correct lengths,formats and valid character set is used,
    if not they would generate a error alert to the user and no changes to the database would be made.
    If they are valid, it will check if the email or username are already in the database, if they are, it will return an error
    If they are not in the database, it will hash the password and add them to the database and redirect to the decks page
    '''
    if request.method == 'POST':

        #Secondary check after the frontend checks, to further check if all the fields are filled out
        if request.form.get('username') and request.form.get('email') and request.form.get('password1') and request.form.get('password2'):
            #Assign the values from the frontend to the local variables
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password1')
            confirm_password = request.form.get('password2')
            #Checks if the email,username and passwords are valid, if not they would be redirected to the register page with an error
            #each check function returns a tuple, the first value contains the true or false and second contains the reason
            if check_email(email)[0] and check_username(username)[0] and check_password(password,confirm_password)[0]:

                #Check if email or username are in the database
                #If both are not in the database, add them to the database
                #If either are in the database, return an error

                #Check if the email already exists in the database
                if check_email_exists(email):
                    flash('Email already exists, Login instead?',category = 'danger')
                    return redirect(url_for('auth.register'))

                #Check if the username already exists in the database
                if check_username_exists(username):
                    flash('Username already exists, choose another',category='danger')
                    return redirect(url_for('auth.register'))
                
                #If the data passes the checks above, add them to the database
                try:
                    #Hash the password, create a new user object and add it to the database and add it to the database
                    new_user = User(username=username,email=email,password=generate_password_hash(password,method='sha256'))
                    db.session.add(new_user)
                    db.session.commit()
                except:
                    flash('Error in creating the account, please try again')

                #if they are successful in the checks above, and are added to the database, then login the user
                try:
                    login_user(new_user,remember=True)#Stores a cookie
                except Exception as e:
                    flash('Error logging in user, after registeration. Try logging in manually error: {}'.format(e),category='danger')
                
                flash('Account successfully created',category='success')
                return redirect(url_for('decks.decks_route'))
            else:
                try:
                    #If the mutltiple functions return error message they are added together
                    error = check_email(email)[1] + ' ' + check_username(username)[1] +' '+ check_password(password,confirm_password)[1]
                    flash(error,category='danger')
                    return render_template("register.html")
                except:
                    flash('Error, Please try again',category='danger')

                return render_template("register.html")
        else:
            flash('Please fill out all fields',category='danger')
        
    #renders the register.html template for users who visit the /auth/register link
    return render_template("register.html")


@login_required
@auth.route('/logout')
def logout():
    '''
    This will log out a user, the logout_user is a function from flask_login
    '''
    logout_user()
    flash('Successfully logged out',category='success')
    return redirect(url_for('auth.login'))
