from . import socketio

@socketio.on('audio_chunk')
def handle_audio_chunk(audio_chunk):
    print('Received audio chunk')

    # Process the audio_chunk here
    # For real-time processing, you might buffer these chunks and process periodically
    # Or if your processing can be done in real-time, handle it directly

    socketio.emit('transcription', {'text': 'Processed transcription here'})
