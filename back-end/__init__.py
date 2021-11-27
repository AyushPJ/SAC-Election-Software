from flask import Flask, request, redirect
from flask_cors import CORS



def create_app():
    app = Flask("SAC-Election-Software")
    CORS(app)
    app.config.from_mapping(
        DATABASE_NAME = "SAC-Election",
        SECRET_KEY = "dev",
    )
    
    
    
    from . import db 
    db.init_app(app)

    from . import candidates
    app.register_blueprint(candidates.bp)

    from . import vote
    app.register_blueprint(vote.bp)


    # @app.route("/", methods=["GET"])
    # def index():
    #     return redirect("/vote/genSec")
        

    return app
    

    