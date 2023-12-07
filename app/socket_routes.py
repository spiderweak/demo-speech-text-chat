from collections import deque
from . import socketio
import logging
import tempfile
import os

import time
from datetime import datetime

from .audio_processing import AudioTranscriptionManager

# Buffer for accumulating audio data
transcription_manager = AudioTranscriptionManager()

@socketio.on('audio_chunk')
def handle_audio_chunk(received_data):

    # Decode audio blob
    audio_data = received_data

    # Convert send date to a valid filename
    filename_date = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename_date}.webm"  # Replace with the appropriate extension

    # Write to file
    with open(filename, 'wb') as file:
        file.write(audio_data)

    print(f"Audio blob saved as {filename}")

    try:
        transcription_manager.append_audio(filename)
        transcription = transcription_manager.get_current_transcription()
        socketio.emit('transcription', {'text': transcription})
    except RuntimeError as re:
        raise

@socketio.on('start_processing')
def switch_to_llm(received_data):

    time.sleep(3)

@socketio.on('chatbot_response')
def handle_my_custom_event(data):
    # Your logic here
    socketio.emit('backend_message', 'This is a message from the backend')