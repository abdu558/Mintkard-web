from flask import Blueprint, render_template,request,url_for,redirect,flash #Delete markup later its used to send html code with flask 
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User#,db
from flask_login import login_user,login_required,logout_user,current_user
from . import db #Import the User class from the models file
import re
#CHECK IF ABOVE ONE IS CORRECT

#flask setup code that registers auth file with init file/app
auth = Blueprint('auth', __name__)


def check_email(email):
    '''r is raw string, this is using the re module to allow any valid character with a @ and a . in the string
    ^ means start of string
    [a-zA-Z0-9_.+-] means any alphabet or number and the 4 symbols which are allowed in an email
    the + sumbol means that the length of the square brackets must be 1 character or longer, so empty spaces get rejected
    the \ will let the period be trated as a period rather than special regex character
    the +$ will mean it represents the endof the domain name of the email
    
    International emails will not work
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
    # Checks for invalid characters
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

    elif not valid_char(password):
        error = "Invalid characters used, please only use characters,numbers and -\.@`{}_~'+/=?!#$%&^"    

    #If there is an error, return the error, if not, return None and True which would let the user continue/add to the database or login
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
        return True;return False

def check_username_exists(username):
    '''
    Checks if the username is already in the database
    Returns true if a username match is found, else it would return false
    '''
    if User.query.filter_by(username=username).first():
        return True;return False
    

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
            if not check_email_exists(email):
                flash('Email is not registered, Register instead?',category = 'danger')
                return redirect(url_for('auth.register'))
            
            if email == User.query.filter_by(email=email).first().email and check_password_hash(User.query.filter_by(email=email).first().password,password):#Why 0
                print('------')
                print(User.query.filter_by(email=email).first().password,password)
                print(User.query.filter_by(email=email))
                print(User.query.filter_by(email=email).first())
                print('-------')
                #print(check_password_hash(User.query.filter_by(email=email).first().password,password)[0])
            else:
                flash('Email or password is incorrect',category='danger')
                return redirect(url_for('auth.login'))


            try:
                user = User.query.filter_by(email=email).first()
                login_user(user)
            except Exception as e:
                flash('Error logging in user: {}'.format(e),category='danger')
                return redirect(url_for('auth.login'))

            flash('You were successfully logged in',category='success')
            return redirect(url_for('decks.decks_route'))


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

                if check_email_exists(email):
                    flash('Email already exists, Login instead?',category = 'danger')
                    return redirect(url_for('auth.register'))

                if check_username_exists(username):
                    flash('Username already exists, choose another',category='danger')
                    return redirect(url_for('auth.register'))
                
                #adds to the database
                try:
                    new_user = User(username=username,email=email,password=generate_password_hash(password,method='sha256'))
                    db.session.add(new_user)
                    db.session.commit()
                except:
                    flash('Error in creating the account, please try again')
                login_user(new_user,remember=True)#Changes remember me to the option of ticked
                flash('Account successfully created',category='success')
                return redirect(url_for('decks.decks_route'))
            else:
                try:
                    #If the mutltiple functions return error message seperate them with a comma, if they are empty do not add a comma 
                    error = check_email(email)[1] + check_username(username)[1] + check_password(password,confirm_password)[1]
                    flash(error,category='danger')
                    return render_template("register.html")
                except:
                    flash('ERROR PLEASE TRY AGAIN',category='danger')

                return render_template("register.html")

        flash('Please fill out all fields',category='danger')
        
    #Returns the template to users who visit /register link
    return render_template("register.html")

#Add a button to do this
@login_required
@auth.route('/logout')
def logout():
    '''
    This will log out a user
    '''
    logout_user()
    flash('Successfully logged out')
    return redirect(url_for('auth.login'))
