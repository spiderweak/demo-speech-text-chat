from collections import deque
from . import socketio

import logging

import time
from datetime import datetime

from .audio_processing import AudioTranscriptionManager
from .text_processing import Conversation

# Buffer for accumulating audio data
transcription_manager = AudioTranscriptionManager()
conversation = Conversation()

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

    logging.info(f"Audio blob saved as {filename}")

    try:
        transcription_manager.append_audio(filename)
        transcription = transcription_manager.get_current_transcription()
        socketio.emit('transcription', {'text': transcription})
    except RuntimeError as re:
        raise


@socketio.on('start_processing')
def switch_to_llm(received_data):
    """
        TODO:
         - Implement control on other socket
         - Fix Prompt engineering
         - Proper review of response, the functionality is not well writtend for now
         - Async would be way better
    """

    time.sleep(3) # This should be temporary, TODO : Implement control on other socket

    #corrected_input = refactor_input(transcription_manager.get_current_transcription()) # TODO : Fix prompt engineering
    corrected_input = transcription_manager.get_current_transcription()

    socketio.emit('correction', corrected_input)
    conversation.init_message(corrected_input)

    answer = conversation.respond()
    socketio.emit('bot_message', answer)


@socketio.on('user_message')
def handle_message(received_data):
    answer = conversation.reception(received_data)
    socketio.emit('bot_message', answer)
