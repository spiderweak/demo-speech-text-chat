import logging

from .. import socketio
from ..custom_exceptions import MissingPackageError
from ..audio_processing import AudioTranscriptionManager

DEFAULT_TIMEOUT = 8 # in seconds

def process_transcription(filename: str, transcription_manager: AudioTranscriptionManager, session_id: str):
    """Process the transcription of an audio file.

    Args:
        filename (str): The path to the audio file to be transcribed.
        transcription_manager (AudioTranscriptionManager): The manager handling audio transcriptions.
        session_id (str): The ID of the current session.

    Raises:
        Exception: Propagates exceptions that occur during processing.
        TimeoutError: If the thread processing the transcription exceeds the allowed time.
    """

    if not transcription_manager.ffmpeg_installed:
        logging.warning("ffmpeg package is not installed on the system, the transcription will be unavailable")
        raise MissingPackageError("ffmpeg not installed on system")

    try:
        thread = transcription_manager.append_audio(filename)
        thread.join(timeout=DEFAULT_TIMEOUT)

        if thread.is_alive():
            logging.error(f"Processing thread for session {session_id} is taking longer than expected.")
            raise TimeoutError(f"Timeout reached when processing thread {thread} for session {session_id}")

        transcription = transcription_manager.transcription
        socketio.emit('transcription', {'text': transcription}, to=session_id)

    except Exception as ex:
        logging.error(f"Error processing transcription: {ex}")
        raise
