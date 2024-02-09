"""
audio_processing.py

This module handles the processing and transcription of audio data. It includes the AudioTranscriptionManager class, 
which manages audio blobs, merges them, and transcribes the merged audio using the Whisper model.
"""

import os
import subprocess
import tempfile
import threading
import logging
import whisper

from collections import deque
from datetime import datetime
from typing import Optional, Deque

from .utils import purge_file, check_ffmpeg_installed

# Load Whisper model globally.
audio_model = whisper.load_model("base")


class AudioTranscriptionManager:
    """Manages the transcription of audio data for a session.

    This class handles audio blobs, stores them in a queue, and uses the Whisper model for transcription. 
    It also manages a temporary folder for storing audio files and keeps track of the session ID.

    Attributes:
        transcription (str): The current transcription text.
        audio_blobs (deque): A queue of audio blob file paths.
        model (whisper.Whisper): The Whisper model used for transcription.
        _temp_folder (tempfile.TemporaryDirectory): The temporary folder for audio files.
        temp_folder_name (str): The name/path of the temporary folder.
        _session_id (str): The ID of the session associated with this manager.
    """

    def __init__(self, temp_folder: Optional[tempfile.TemporaryDirectory] = None, session_id : Optional[str] = None):
        """Initializes the AudioTranscriptionManager with an optional temporary folder and session ID.

        If no temporary folder is provided, a new one is created. The temporary folder is used for storing audio files.
        The session ID, if provided, is used to identify the session associated with this manager.

        Args:
            temp_folder (Optional[tempfile.TemporaryDirectory]): The temporary folder for storing audio files.
            session_id (Optional[str]): The ID of the session.
        """

        self.transcription = ""
        self.audio_blobs: Deque[str] = deque()
        self.model : whisper.Whisper = audio_model

        self._temp_folder = temp_folder or tempfile.TemporaryDirectory()
        self.temp_folder_name = self._temp_folder.name

        self._session_id = session_id or ""

        self.ffmpeg_installed = check_ffmpeg_installed()


    @property
    def transcription(self) -> str:
        """
        Gets the current transcription text.

        Returns:
            str: The current transcription text.
        """
        return self._transcription


    @transcription.setter
    def transcription(self, transcription: str):
        """Sets the current transcription text.

        Args:
            transcription (str): The transcription text to be set.
        """
        self._transcription = transcription


    def append_audio(self, blob_file: str) -> threading.Thread:
        """Appends an audio blob file to the queue and initiates merging and transcription if necessary.

        This method adds a new audio blob to the queue. If the queue exceeds 10 blobs, the oldest blob is removed 
        and its file is purged. It then calls the `merge_audio_blobs` method to merge and transcribe the audio.

        Args:
            blob_file (str): The file path of the audio blob to be appended.

        Returns:
            threading.Thread: The thread initiated for merging and transcribing the audio blobs.
        """
        self.audio_blobs.append(blob_file)

        if len(self.audio_blobs) > 10:
            oldest_blob = self.audio_blobs.popleft()
            try:
                purge_file(oldest_blob)
            except Exception as e:
                logging.error(f"Error purging audio blob: {e}")

        thread = self.merge_audio_blobs()

        return thread

    def merge_audio_blobs(self) -> threading.Thread:
        """Merges multiple audio blobs into a single audio file using FFmpeg and starts the transcription process.

        This method concatenates audio files listed in `self.audio_blobs` using FFmpeg, then starts a new thread to 
        transcribe the merged audio file. The merged file is named with a current timestamp.

        Returns:
            threading.Thread: The thread object for the transcription process.
        """

        filename_date = datetime.now().strftime("%Y%m%d_%H%M%S")
        list_file = os.path.join(self.temp_folder_name, "filelist.txt")

        with open(list_file, 'w') as f:
            for file_path in self.audio_blobs:
                f.write(f"file '{file_path}'\n")
        current_audio_file = os.path.join(self.temp_folder_name, f"combined-{filename_date}.webm")

        ffmpeg_cmd = ["ffmpeg", "-f", "concat", "-safe", "0", "-i", list_file, "-c", "copy", current_audio_file]

        try:
            subprocess.run(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        except subprocess.CalledProcessError as e:
            logging.error(f"An error occurred during FFmpeg processing: {e}")
            raise
        except FileNotFoundError as fnfe:
            logging.error(f"SubProcess Raised a FileNotFound Error, check that ffmpeg is installed on your system: {fnfe}")
            raise

        logging.debug("Merging Done, starting transcription thread")
        thread = threading.Thread(target=self.transcribe_audio, args=(current_audio_file,))
        thread.start()
        logging.debug(f"Transcription thread {thread.ident} started for file {current_audio_file}")

        purge_file(list_file)

        return thread


    def transcribe_audio(self, current_audio_file : str):
        """Transcribes the given audio file using the Whisper model.

        Args:
            current_audio_file (str): The path to the audio file to be transcribed.

        Raises:
            Exception: Propagates any exceptions that occur during transcription.
        """
        try:
            result = self.model.transcribe(current_audio_file, word_timestamps=True)
            self.transcription = str(result['text'])
            logging.debug("Transcription completed successfully.")
            purge_file(current_audio_file)
        except Exception as e:
            logging.error(f"Error during transcription: {e}")
            raise


    def renew(self):
        """Resets the transcription manager, clearing any stored transcriptions
        and audio blobs, and cleans up related temporary files.
        """

        self.transcription = ""

        while self.audio_blobs:
            blob = self.audio_blobs.popleft()
            purge_file(blob)

        list_file = os.path.join(self.temp_folder_name, "filelist.txt")
        purge_file(list_file)
