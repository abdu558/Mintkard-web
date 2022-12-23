from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '/B?E(G+KbPeShVmYq3t6w9z$C&F)J@Mc'
    app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    from .views import views
    from .auth import auth
    from .decks import decks

    #This registers the blueprint allowing routes to put into seperate files
    app.register_blueprint(views, url_prefix='/')
    #This will add /auth before all routes in the decks file
    app.register_blueprint(auth, url_prefix='/auth')
    #This will add /decks before all routes in the decks file
    app.register_blueprint(decks, url_prefix='/decks')

    

    from .models import User, Deck, Card

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(id)
    
    app.app_context().push()
    print(User.query.all())
    # if not path.exists('/data.db'):
    #     with app.app_context():
    #         db.create_all()
    #         print('database has been created')
    return app
