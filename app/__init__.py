"""Module for initializing the Flask application and its components."""

from flask import Flask
from flask_socketio import SocketIO

from .routes import setup_routes

socketio = SocketIO(manage_session = True)

def create_app() -> Flask:
    """
    Create and configure an instance of the Flask application.

    Returns:
        Flask: The created Flask application.
    """

    app = Flask(__name__)

    socketio.init_app(app)
    setup_routes(app)

    # Importing socket routes here to avoid circular dependencies
    from . import socket_routes

    return app

