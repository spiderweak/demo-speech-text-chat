"""Module for initializing the Flask application and its components."""

import logging
from flask import Flask
from flask_socketio import SocketIO

from .routes import setup_routes

socketio = SocketIO(manage_session = True)

def create_app(headless: bool = False) -> Flask:
    """
    Create and configure an instance of the Flask application.

    Returns:
        Flask: The created Flask application.
    """

    app = Flask(__name__)
    socketio.init_app(app)

    logging.debug("Socket IO initialized")

    if not headless:
        setup_routes(app)
        logging.debug("Serving Web page")

    # Importing socket routes here to avoid circular dependencies
    from . import socket_routes
    logging.debug("Loading socket routes")

    return app

