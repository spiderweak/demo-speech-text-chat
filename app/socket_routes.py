from collections import deque
from . import socketio
import whisper
import logging
import tempfile
import os

from collections import deque

from pydub import AudioSegment

model = whisper.load_model("base")

# Buffer for accumulating audio data
audio_buffer = deque()

@socketio.on('audio_chunk')
def handle_audio_chunk(audio_chunk):

    audio_buffer.append(audio_chunk)

    united_audio_file = merge_audio_blobs(audio_buffer)

    print(f"Audio chunk saved to {united_audio_file}, size: {os.path.getsize(united_audio_file)} bytes")

    try:
        # Process the saved audio file
        result = model.transcribe(united_audio_file, word_timestamps=True)

        transcription = result["text"]

        # Emit the transcription result
        socketio.emit('transcription', {'text': transcription})
    except RuntimeError as re:
        print(re)

    os.remove(united_audio_file)

def merge_audio_blobs(blobs: deque):
    """
    Merge multiple WebM audio blobs into a single audio file using FFmpeg.

    Args:
        blobs (list of bytes): The list of WebM audio blobs.

    Returns:
        bytes: The merged audio in WebM format.
    """

def merge_mp3_files(files: deque):
    # Initialize an empty audio segment
    combined = AudioSegment.empty()

    # Loop through each file and append it to the combined segment
    for file in files:
        audio = AudioSegment.from_mp3(file)
        combined += audio

    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3', dir='.') as temp_file:
        temp_file.write(combined)

    return temp_file.name
