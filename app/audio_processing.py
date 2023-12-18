from collections import deque
import tempfile
import whisper
import os
import subprocess
from datetime import datetime
import tempfile

audio_model = whisper.load_model("base")

class AudioTranscriptionManager:
    def __init__(self, temp_folder: tempfile.TemporaryDirectory, session_id = ""):
        self.transcription = ""
        self.audio_blobs = deque()
        self.model = audio_model
        self._temp_folder = temp_folder
        self.temp_folder_name = temp_folder.name
        self._session_id = session_id

    def append_audio(self, blob_file):
        # Add blob to the queue
        self.audio_blobs.append(blob_file)
        if len(self.audio_blobs) > 10:
            blob = self.audio_blobs.popleft()
            purge_audio(blob)
        self.merge_audio_blobs()

    def merge_audio_blobs(self):
        """
        Merge multiple mp3 audio blobs into a single audio file using FFmpeg.

        Returns:
            str: The merged audio path in str format
        """

        # Initialize an empty audio segment

        filename_date= datetime.now().strftime("%Y%m%d_%H%M%S")

        list_file = os.path.join(self.temp_folder_name, "filelist.txt")

        # Create a list file for FFmpeg
        with open(list_file, 'w') as f:
            for file_path in self.audio_blobs:
                f.write(f"file '{file_path}'\n")


        current_audio_file = os.path.join(self.temp_folder_name, f"combined-{filename_date}.webm")

        # Create the FFmpeg command
        ffmpeg_cmd = ["ffmpeg", "-f", "concat", "-safe", "0", "-i", list_file, "-c", "copy", current_audio_file]

        try:
        # Execute the command
            subprocess.run(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        except subprocess.CalledProcessError as e:
            print(f"An error occurred: {e}")
            raise e

        self.set_current_transcription(current_audio_file)

        purge_audio(current_audio_file)

    def set_current_transcription(self, current_audio_file):
        try:
            result = self.model.transcribe(current_audio_file, word_timestamps=True)
            self.transcription = str(result['text'])
        except:
            pass


    def get_current_transcription(self) -> str:
        return self.transcription

    def renew(self):
        self.transcription = ""
        while self.audio_blobs:
            blob = self.audio_blobs.popleft()
            purge_audio(blob)

        list_file = os.path.join(self.temp_folder_name, "filelist.txt")

        purge_audio(list_file)

def purge_audio(file):
    os.remove(file)