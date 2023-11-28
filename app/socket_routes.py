from . import socketio
import whisper
import io
import uuid
import wave
import logging


model = whisper.load_model("base")

# Buffer for accumulating audio data
audio_buffer = bytearray()

@socketio.on('audio_chunk')
def handle_audio_chunk(audio_chunk):
    global audio_buffer

    # Append chunk to the buffer
    audio_buffer.extend(audio_chunk)

    # Check if the buffer has enough data to process (5 seconds of audio)
    if len(audio_buffer) >= 882000:
        process_audio_buffer()



def process_audio_buffer():
    global audio_buffer

    temp_filename = f"temp_{uuid.uuid4()}.wav"

    with wave.open(temp_filename, 'wb') as temp_file:
        temp_file.setparams((2, 2, 44100, 0, 'NONE', 'NONE'))
        temp_file.writeframes(audio_buffer)

    audio_buffer.clear()

    # Process the saved audio file
    result = model.transcribe(temp_filename)
    transcription = result["text"]

    # Emit the transcription result
    socketio.emit('transcription', {'text': transcription})
    print(transcription)
