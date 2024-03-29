"""Module for handling Socket.IO events in the Flask application.

This module sets up event handlers for various Socket.IO events such as connecting, 
disconnecting, and receiving data from the client. It manages sessions and orchestrates 
audio processing and text conversation handling.
"""

import logging
import tempfile
from typing import Dict, Tuple, Any

from flask import request
from . import socketio
from .audio_processing import AudioTranscriptionManager, process_transcription
from .text_processing import Conversation
from .utils import generate_filename, save_data_to_file, convert_audio_data
from .utils.custom_exceptions import MissingPackageError

from .datatypes import Message

# Dictionary to manage session states and associated objects for each client.
session_managers: Dict[str, Tuple[AudioTranscriptionManager, Conversation]] = {}

@socketio.on('connect')
def handle_connect():
    """Handle a new client connection by initializing session managers."""

    session_id = request.sid  # type:ignore
    temp_folder = tempfile.TemporaryDirectory()

    session_managers[session_id] = (AudioTranscriptionManager(temp_folder, session_id=session_id), Conversation(session_id=session_id))

    starting_message = Message("info", """Welcome to Chronos Chat, don't hesitate to ask us any question,
                  we inform you that the real time transcription functionality is only available for 
                  30s speech, if you need to talk for more than 30s, please toggle the "disable real time transcription"
                  button at the bottom of the window. Click this message to dismiss it.""")

    starting_message_dict = {
                "message_id": str(starting_message.id),
                "sender" : starting_message.emitter,
                "content": starting_message.content
            }

    socketio.emit('message', starting_message_dict, to=session_id)


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection by cleaning up resources."""
    session_id = request.sid  # type: ignore
    if session_id in session_managers:
        audio_transcription_manager, _ = session_managers.pop(session_id)
        audio_transcription_manager.renew()  # Cleanup


@socketio.on('audio_chunk')
def handle_audio_chunk(received_data: Any):
    """Handle an audio chunk sent by a client.

    Args:
        received_data (bytes): The received audio data.
    """
    session_id = request.sid  # type: ignore
    transcription_manager, _ = session_managers.get(session_id, (None, None))

    if not isinstance(transcription_manager, AudioTranscriptionManager):
        logging.error(f"Session manager not found for session ID: {session_id}")
        return

    filename = generate_filename(transcription_manager.temp_folder_name)
    save_data_to_file(received_data, filename)

    try:
        process_transcription(filename, transcription_manager, session_id)
    except MissingPackageError:
        forwarded_message = Message("error", "Missing package, audio transcription not available")

        forwarded_message_dict = {
            "message_id": str(forwarded_message.id),
            "sender" : forwarded_message.emitter,
            "content": forwarded_message.content
        }

        socketio.emit('message', forwarded_message_dict, to=session_id)


@socketio.on('audio_file')
def handle_audio_file(received_data: Any):
    """Handle a complete audio file sent by a client.

    Args:
        received_data (bytes): The received audio file
    """
    session_id = request.sid  # type: ignore
    transcription_manager, _ = session_managers.get(session_id, (None, None))

    if not isinstance(transcription_manager, AudioTranscriptionManager):
        logging.error(f"Session manager not found for session ID: {session_id}")
        return

    origin = generate_filename(transcription_manager.temp_folder_name, extension="wav")
    filename = generate_filename(transcription_manager.temp_folder_name)
    save_data_to_file(received_data, origin)
    convert_audio_data(origin = origin, destination = filename)

    try:
        process_transcription(filename, transcription_manager, session_id, timeout=120)
    except MissingPackageError:
        forwarded_message = Message("error", "Missing package, audio transcription not available")

        forwarded_message_dict = {
            "message_id": str(forwarded_message.id),
            "sender" : forwarded_message.emitter,
            "content": forwarded_message.content
        }

        socketio.emit('message', forwarded_message_dict, to=session_id)


@socketio.on('user_message')
def handle_text_message(received_data: Any):
    """Handle a text message received from the user via Socket.IO.

    Args:
        received_data: The text data received from the user.
    """
    session_id = request.sid # type:ignore
    managers = session_managers.get(session_id)

    if not managers:
        logging.error(f"No session managers found for session ID: {session_id}")
        return

    transcription_manager, conversation_manager = managers

    if not isinstance(transcription_manager, AudioTranscriptionManager):
        logging.error(f"Invalid audio transcription manager for session ID: {session_id}")
        return
    transcription_manager.renew()

    if not isinstance(conversation_manager, Conversation):
        logging.error(f"Invalid conversation manager for session ID: {session_id}")
        return

    logging.debug(f"Received message data: {received_data}")

    # Send message to conversation manager, receive response
    code, message = conversation_manager.reception(received_data)

    response = {
                "message_id": str(message.id),
                "sender" : message.emitter,
                "content": message.content
            }

    socketio.emit('message', response, to=session_id)

    if code != 200:
        logging.debug(f"Error {code}: {response}")
    else:
        logging.debug(f"LLM response built: {response}")
