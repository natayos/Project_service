from flask import Flask;
from flask_cors import CORS;
import os;

def create_app():
    app = Flask(__name__);
    CORS(app);
    from .controller import controller;
    app.register_blueprint(controller, url_prefix = '/');
    
    return app;