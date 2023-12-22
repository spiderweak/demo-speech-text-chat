import os
import requests
import logging
from dotenv import load_dotenv
from datetime import datetime
from llama_cpp import Llama

from . import socketio
from .audio_processing import AudioTranscriptionManager
from .custom_exceptions import TimeoutError, MissingPackageError

DEFAULT_TIMEOUT = 8 # in seconds

def generate_audioblob_filename(folder_name: str) -> str:
    """Generate a filename for an audio blob using the current date and time.

    This function creates a filename with a timestamp format based on the current date and time,
    ensuring uniqueness for each file. The filename will have a '.webm' extension, which can be
    replaced with an appropriate extension if necessary.

    Args:
        folder_name (str): The name of the folder where the audio blob will be saved.

    Returns:
        str: The generated filename, which includes the folder path, a timestamp, and the '.webm' extension.
    """

    filename_date = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(folder_name, f"{filename_date}.webm")

    return filename


def process_transcription(filename: str, transcription_manager: AudioTranscriptionManager, session_id):
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


def save_data_to_file(data: bytes, filename: str):
    """Save data to a file.

    Args:
        data (bytes): The audio data to save.
        filename (str): The filename where the data should be saved.
    """

    with open(filename, 'wb') as file:
        file.write(data)
        logging.debug(f"(Audio) data saved as {filename}")


def load_text_model(model_path = None, model_url = "https://huggingface.co/TheBloke/zephyr-7B-beta-GGUF/resolve/main/zephyr-7b-beta.Q6_K.gguf"):
    """Load the model, downloading it if it's not already present."""
    load_dotenv()

    model_path = os.getenv("LLAMA_MODEL_PATH")

    if model_path is None:
        raise EnvironmentError(f"LLAMA_MODEL_PATH environment variable not set")

    if not os.path.exists(model_path):
        model_url = os.getenv("LLAMA_MODEL_URL") or model_url
        logging.warning(f"Model not found at {model_path}, downloading from {model_url}...")

        response = requests.get(model_url)

        if response.status_code == 200:
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            with open(model_path, 'wb') as model_file:
                model_file.write(response.content)
        else:
            raise Exception(f"Failed to download model. HTTP status code: {response.status_code}")
    else:
        logging.debug(f"Model found at {model_path}, loading...")

    try:
        llm = Llama(model_path=model_path, n_ctx=40960, n_batch=128, verbose=False)
        return llm
    except ValueError as ve:
        logging.error(ve)
        raise
