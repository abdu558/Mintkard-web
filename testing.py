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

    #If there is an error, return the error, if not return None and True which would let the user continue/add to the database or login
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


    #If there is an error, return the error, if not return None and True which would let the user continue/add to the database or login
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
    
#Get all the errors from the functions
#Get all the errors from the functions
    email_error = check_email(request.form.get('email'))
    username_error = check_username(request.form.get('username'))
    password_error = check_password(request.form.get('password'), request.form.get('confirm_password'))
    
    #Check if there are any errors
    if email_error[0] == False or username_error[0] == False or password_error[0] == False:
        #If there are errors, return the errors to the user
        return render_template("login.html",email_error=email_error[1],username_error=username_error[1],password_error=password_error[1])
    else:
        #If there are no errors, return the user to the home page
        return redirect(url_for('views.home'))



    if email_error[0] and username_error[0] and password_error[0]:
        #If there are no errors, add the user to the database
        user = User(email=request.form.get('email'),username=request.form.get('username'),password=generate_password_hash(request.form.get('password'),method='sha256'))
        db.session.add(user)
        db.session.commit()
        #This will redirect the user to the login page
        return redirect(url_for('auth.login'))
    else:
        #If there is an error, return the error and the page will reload with the error
        return render_template('register.html',error=email_error[1] or username_error[1] or password_error[1])
    