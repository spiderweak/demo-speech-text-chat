from . import socketio

import logging

from flask import request

import time
from datetime import datetime

from .audio_processing import AudioTranscriptionManager
from .text_processing import Conversation

from typing import Dict, Tuple

import tempfile

session_managers: Dict[str, Tuple[AudioTranscriptionManager, Conversation]] = {}

@socketio.on('connect')
def handle_connect():
    session_id = request.sid  # type:ignore
    temp_folder = tempfile.TemporaryDirectory()
    session_managers[session_id] = (AudioTranscriptionManager(temp_folder, session_id=session_id), Conversation())

@socketio.on('disconnect')
def handle_disconnect():
    session_id = request.sid  # type:ignore
    if session_id in session_managers:
        audio_transcription_manager, conversation_manager = session_managers.pop(session_id)
        audio_transcription_manager.renew()  # Cleanup


@socketio.on('audio_chunk')
def handle_audio_chunk(received_data):
    session_id = request.sid # type:ignore
    transcription_manager, conversation_manager = session_managers.get(session_id) # type:ignore

    if type(transcription_manager) is not AudioTranscriptionManager:
        logging.error("Session manager not found for session ID: {}".format(session_id))
        return

    # Decode audio blob
    audio_data = received_data

    temp_folder = transcription_manager.temp_folder_name

    # Convert send date to a valid filename
    filename_date = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{temp_folder}/{filename_date}.webm"  # Replace with the appropriate extension

    # Write to file
    with open(filename, 'wb') as file:
        file.write(audio_data)

    logging.info(f"Audio blob saved as {filename}")

    try:
        transcription_manager.append_audio(filename)
        transcription = transcription_manager.get_current_transcription()
        socketio.emit('transcription', {'text': transcription}, to=session_id)
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
    session_id = request.sid # type:ignore
    transcription_manager,conversation_manager = session_managers.get(session_id) # type:ignore


    time.sleep(3) # This should be temporary, TODO : Implement control on other socket

    #corrected_input = refactor_input(transcription_manager.get_current_transcription()) # TODO : Fix prompt engineering
    corrected_input = transcription_manager.get_current_transcription()

    socketio.emit('correction', corrected_input)
    conversation_manager.init_message(corrected_input)

    answer = conversation_manager.respond()
    socketio.emit('bot_message', answer)


@socketio.on('user_message')
def handle_message(received_data):
    session_id = request.sid # type:ignore
    transcription_manager,conversation_manager = session_managers.get(session_id) # type:ignore

    answer = conversation_manager.reception(received_data)
    socketio.emit('bot_message', answer, to=session_id)
