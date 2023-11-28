from flask import Flask
from flask_socketio import SocketIO
from .routes import setup_routes

socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    socketio.init_app(app)
    setup_routes(app)
    return app
