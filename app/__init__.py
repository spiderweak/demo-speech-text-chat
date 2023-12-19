from flask import Flask
from flask_socketio import SocketIO
from .routes import setup_routes

socketio = SocketIO(manage_session = True)

def create_app():

    app = Flask(__name__)
    socketio.init_app(app)

    setup_routes(app)

    from . import socket_routes

    return app
