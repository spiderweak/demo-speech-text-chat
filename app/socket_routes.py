from . import socketio
import whisper
import io
import uuid
import wave
import logging
import tempfile
import os

model = whisper.load_model("base")

# Buffer for accumulating audio data

@socketio.on('audio_chunk')
def handle_audio_chunk(audio_chunk):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.webm', dir='.') as temp_file:
        temp_file.write(audio_chunk)
        temp_file_path = temp_file.name

    print(f"Audio chunk saved to {temp_file_path}, size: {os.path.getsize(temp_file_path)} bytes")

    # Process the saved audio file
    result = model.transcribe(temp_file_path)
    transcription = result["text"]

    # Emit the transcription result
    socketio.emit('transcription', {'text': transcription})

    os.remove(temp_file_path)