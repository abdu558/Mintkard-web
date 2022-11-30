from flask import Blueprint

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return "<p>login</p>"


@auth.route('/register')
def login():
    return "<p>login</p>"


@auth.route('/logout')
def login():
    return "<p>login</p>"
