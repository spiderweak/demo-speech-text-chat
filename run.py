from app import create_app, socketio

app = create_app()

if __name__ == '__main__':
    # Passed allow_unsafe_werkzeug=True to disable error : RuntimeError: The Werkzeug web server is not designed to run in production.
    # TODO: Fix this for production
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
#    app.run(host='0.0.0.0', port=5000, debug=True)

