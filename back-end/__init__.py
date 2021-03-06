from flask import Flask
from flask.helpers import url_for
from flask.templating import render_template
from flask_cors import CORS
from flask_login import LoginManager
import os



def create_app():
    app = Flask("SAC-Election-Software")
    CORS(app)
    import json
    secretsJSON = open('secrets.json', 'r')
    secrets = json.load(secretsJSON)
    secretsJSON.close()
    app.config.from_mapping(
        DATABASE_NAME = "SAC-Election",
        SECRET_KEY = secrets['SECRET_KEY'],
        GOOGLE_CLIENT_ID = secrets['GOOGLE_CLIENT_ID'],
        GOOGLE_CLIENT_SECRET = secrets['GOOGLE_CLIENT_SECRET'],
        APPLICATIONS = dict(status=False,open = None, close = None), #status = False/True/Automatic
        VOTING = dict(status=False,open = None, close = None) #status = False/True/Automatic
    )


    app.secret_key = app.config['SECRET_KEY']
    
    login_manager = LoginManager()
    login_manager.init_app(app)

    from . import db 
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import admin
    app.register_blueprint(admin.bp)

    from . import student
    app.register_blueprint(student.bp)

    from . import applications
    app.register_blueprint(applications.bp)

    from . import vote
    app.register_blueprint(vote.bp)
    @app.errorhandler(404)
    def page_not_found(e):
        #note that we set the 404 status explicitly
        return render_template('error.html', msg="The page you are looking for might have been removed had its name changed or is temporarily unavailable.", title="Page not found", statusCode="404" ), 404


    from .user import User
    @login_manager.user_loader
    def load_user(userID):
        user = User.get(userID)
        return user

    @app.route("/", methods=["GET"])
    def index():
            return render_template("welcome.html")
    return app
    

    