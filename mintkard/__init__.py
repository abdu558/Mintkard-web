from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '/B?E(G+KbPeShVmYq3t6w9z$C&F)J@Mc'

    from .views import views
    from .auth import auth
    from .decks import decks
    
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/auth/')
    app.register_blueprint(decks, url_prefix='/decks/')


    return app
