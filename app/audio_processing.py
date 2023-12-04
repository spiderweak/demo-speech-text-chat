from collections import deque
import tempfile
import whisper
import os
import subprocess
from datetime import datetime

class AudioTranscriptionManager:
    def __init__(self):
        self.transcription = ""
        self.audio_blobs = deque()
        self.model = whisper.load_model("base")

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

        list_file = 'filelist.txt'
        filename_date= datetime.now().strftime("%Y%m%d_%H%M%S")
        current_audio_file = f"combined-{filename_date}.webm"

        # Create a list file for FFmpeg
        with open(list_file, 'w') as f:
            for file_path in self.audio_blobs:
                f.write(f"file '{file_path}'\n")

        # Create the FFmpeg command
        ffmpeg_cmd = f"ffmpeg -f concat -safe 0 -i {list_file} -c copy {current_audio_file}"

        try:
        # Execute the command
            subprocess.run(ffmpeg_cmd, check=True, shell=True)
        except subprocess.CalledProcessError as e:
            print(f"An error occurred: {e}")
            raise e

        self.set_current_transcription(current_audio_file)

        purge_audio(current_audio_file)

    def set_current_transcription(self, current_audio_file):
        try:
            result = self.model.transcribe(current_audio_file, word_timestamps=True)
            self.transcription = result['text']
        except:
            pass


    def get_current_transcription(self):
        return self.transcription


def purge_audio(file):
    os.remove(file)