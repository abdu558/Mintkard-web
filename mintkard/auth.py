from flask import Blueprint

auth = views = Blueprint('views', __name__)

@auth.route("hello")