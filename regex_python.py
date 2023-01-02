import re
#CHECK IF ABOVE ONE IS CORRECT

#flask setup code that registers auth file with init file/app


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
        return match,'Please a valid email'

#INTEGRATE THIS 
def valid_char(user_input):
    '''
    Returns True if it is using a valid set of characters
    '''
    # Check for invalid characters
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
