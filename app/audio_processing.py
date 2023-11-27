import whisper

def transcribe_audio(file_path):
    model = whisper.load_model("base")

    # Specify the directory where you want to save the file
    result = model.transcribe(file_path)
    transcription = result["text"]
    return transcription