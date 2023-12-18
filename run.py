from app import create_app, socketio
import os
from dotenv import load_dotenv

load_dotenv()

app = create_app()

if __name__ == '__main__':
    # Passed allow_unsafe_werkzeug=True to disable error : RuntimeError: The Werkzeug web server is not designed to run in production.
    # TODO: Fix this for production

    debug_mode = os.getenv('FLASK_DEBUG', 'False') == 'True'
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', '5000'))

    socketio.run(app, host=host, port=port, debug=debug_mode, allow_unsafe_werkzeug=True)

