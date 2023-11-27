from flask import render_template, request, jsonify
from .audio_processing import transcribe_audio
from werkzeug.utils import secure_filename
import os

def setup_routes(app):

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/upload-audio', methods=['POST'])
    def upload_audio():
        if 'audio' in request.files:

            audio_file = request.files['audio']
            filename = secure_filename(audio_file.filename) # type: ignore

            upload_folder = 'minutes'
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            temp_path = os.path.join(upload_folder, filename)

            audio_file.save(temp_path)

            transcription = transcribe_audio(temp_path)

            return jsonify({"transcription": transcription})
        else:
            return jsonify({"error": "No audio file received"}), 400
