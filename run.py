"""Entry point for the Flask application.

This script initializes the Flask application and runs the server with socket.io support.
"""

import os
import logging
import argparse
from dotenv import load_dotenv

from app import create_app, socketio


def configure_logging(log_level: str, log_file: str):
    """Configure the logging for the application."""

    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {log_level}')

    logging.basicConfig(level=numeric_level, filename=log_file, filemode='a')

def load_environment_variables():
    """Load environment variables from the .env file."""

    load_dotenv()

def parse_arguments():
    """Parse command line arguments."""

    parser = argparse.ArgumentParser(description='Run the Flask application with Socket.IO support.')
    parser.add_argument('--log-level', type=str, default='INFO', help='Set the logging level (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL)')
    parser.add_argument('--log-file', type=str, default='log.txt', help='Set the log file location')
    parser.add_argument('--headless', action='store_true', help='Run the server in headless mode (no HTTP routes)')

    return parser.parse_args()


def main():
    """Run the Flask application with Socket.IO support."""

    args = parse_arguments()
    configure_logging(args.log_level, args.log_file)
    load_environment_variables()

    app = create_app(headless=args.headless)

    debug_mode = os.getenv('FLASK_DEBUG', 'False') == 'True'
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', '5000'))
    use_reloader = debug_mode
    log_output = True

    # Passed allow_unsafe_werkzeug=True to disable error : RuntimeError: The Werkzeug web server is not designed to run in production.
    # TODO: Fix unsafe Werkzeug usage for production
    socketio.run(app, host=host, port=port, debug=debug_mode, use_reloader=use_reloader, log_output=log_output, allow_unsafe_werkzeug=True)


if __name__ == '__main__':
    main()