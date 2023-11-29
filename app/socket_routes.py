from collections import deque
from . import socketio
import whisper
import io
import uuid
import wave
import logging
import tempfile
import os

from ffmpeg import FFmpeg
import io
from collections import deque

import asyncio
from pathlib import Path

from ffmpeg import Progress
from ffmpeg.asyncio import FFmpeg

model = whisper.load_model("base")

# Buffer for accumulating audio data
audio_buffer = deque()

@socketio.on('audio_chunk')
def handle_audio_chunk(audio_chunk):

    audio_buffer.append(audio_chunk)

    united_audio = merge_audio_blobs(audio_buffer)

    with tempfile.NamedTemporaryFile(delete=False, suffix='.webm', dir='.') as temp_file:
        temp_file.write(audio_chunk)
        temp_file_path = temp_file.name

    print(f"Audio chunk saved to {temp_file_path}, size: {os.path.getsize(temp_file_path)} bytes")

    try:
        # Process the saved audio file
        result = model.transcribe(temp_file_path, condition_on_previous_text=True)
        transcription = result["text"]

        # Emit the transcription result
        socketio.emit('transcription', {'text': transcription})
    except RuntimeError as re:
        print(re)

    os.remove(temp_file_path)

def merge_audio_blobs(blobs: deque):
    """
    Merge multiple WebM audio blobs into a single audio file using FFmpeg.

    Args:
        blobs (list of bytes): The list of WebM audio blobs.

    Returns:
        bytes: The merged audio in WebM format.
    """

    ffmpeg_command = (
        FFmpeg()
        .option("y")
    )

    # Dynamically add each blob as an input
    for _ in blobs:
        ffmpeg_command = ffmpeg_command.input("pipe:")

    # Specify the output options
    ffmpeg_command = ffmpeg_command.output(
        "pipe:", 
        format='webm', 
        vcodec='copy', 
        acodec='copy'
    )

    print("FFmpeg command:", ffmpeg_command.get_args())

    # Execute the FFmpeg command with the blobs as arguments
    merged_audio, _ = ffmpeg_command.execute()

    return merged_audio