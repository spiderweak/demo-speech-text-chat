# Démo Speech Text Chat

This project is a Flask web application that captures audio from the user's microphone and uses OpenAI's Whisper model for speech-to-text transcription.

## Features

- Record audio directly in the web browser.
- Send the audio data to a Flask server.
- Use Whisper to transcribe the audio to text.
- Display the transcription result on the web page.

# Todo

- Implement actual chatbot
- Various feedback loops to improve the quality of the transcript as well as the questions/answers
- More logging, especially to add conversation to contexts in case further processing is needed
- Real Time Transcription

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

What things you need to install the software and how to install them:

```
python3
pip
virtualenv (optional)
Docker (optional for containerization)
```

### Installing

How to get the app running?

1. Clone the repository:

```bash
git clone https://github.com/spiderweak/demo-speech-text-chat
```

2. Navigate to the project directory:

```bash
cd demo-speech-text-chat
```

3. Create a virtual environment (alternatively, use conda, but please try not to install this directly on your system, it's not a good practice):

```bash
python -m venv .venv
source .venv/bin/activate
```

4. Install the required dependencies:

```bash
pip install -r requirements.txt
```

### Running the Application

Run the application with:

```bash
python run.py
```

Access the web application at `http://127.0.0.1:5000/`.

## Docker Support

If you wish to use Docker for deployment:

1. Build the Docker image:

```bash
docker build -t demo-speech-text-chat .
```

2. Run the Docker container:

```bash
docker run -p 5000:5000 demo-speech-text-chat
```

## Contributing

This project does not accept exterior contributions for now.

## Authors

Antoine ["Spiderweak"](https://github.com/spiderweak) BERNARD

## License

Unless part of the system is incompatible with it, consider this project under CC BY-NC-SA and mostly used for research purposes and teaching.

## Acknowledgments

Thanks to these project, that make most of the project run
- OpenAI for the Whisper model
- Flask
