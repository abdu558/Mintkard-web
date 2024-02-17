from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    
    app.config['SECRET_KEY'] = '/B?E(G+KbPeShVmYq3t6w9z6rshts$C&F)J@Mc'
    app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
    db.init_app(app)

    #Set up for the loginmanager for flask
    login_manager = LoginManager()    
    login_manager.login_view = 'auth.login' #Where does flask redirect the user if they are not logged in
    login_manager.login_message = "Simply login to access this page and get started on your journey to academic success. Don't miss out on the chance to succeed academically! "
    login_manager.init_app(app)#tells login manager the app and it's details, the flask app/project
    
    from .views import views
    from .auth import auth
    from .decks import decks

    #This registers the blueprint allowing routes to put into seperate files
    app.register_blueprint(views, url_prefix='/')

    #This will add /auth before all routes in the auth file
    app.register_blueprint(auth, url_prefix='/auth')
    #This will add /decks before all routes in the decks file
    app.register_blueprint(decks, url_prefix='/decks')


    from .models import User, Deck, Card



    login_manager.init_app(app)
    #tells login manager which app its using

    #tells loginmanager how the user is loaded by looking at the primary key, looks for the primary key by default so no need to specify what id equals
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(id)

    # if not path.exists('/data.db'):
    #     with app.app_context():
    #         db.create_all()
    #         print('database has been created')
    return app


