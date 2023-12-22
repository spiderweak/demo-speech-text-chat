# Démo Speech Text Chat

This project is a Flask web application that captures audio from the user's microphone and uses OpenAI's Whisper model for speech-to-text transcription.

## Features

- Record audio directly in the web browser.
- Send the audio data to a Flask server.
- Use Whisper to transcribe the audio to text.
- Display the transcription result on the web page.
- Working chatbot
- Real Time Transcription
- More logging

# Todo

- Various feedback loops to improve the quality of the transcript as well as the questions/answers
- add conversation to contexts in case further processing is needed

Also:
- Fix unsafe Wekzeug usage for production
- Improve the template as the current responses may not be satisfactory.
- Implement more specific error handling related to Llama model interactions.

And:
- Stream answer

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

What things you need to install the software and how to install them:

```
python3
pip
virtualenv (optional)
ffmpeg (for the audio processing (both this project and openai-whisper))
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

If necessary, you can run this application in headless mode to put your own frontend interface,
don't forget you still need to send your data to the correct backend routes.

```bash
python run.py --headless
```

This last feature has not been extensively tested.

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

As you can do with the non-dockerized version, you can run the project with docker in headless mode:

```bash
docker run -p 5000:5000 demo-speech-text-chat --headless
```

## Interfaces diagram

![interfaces diagram](https://github.com/spiderweak/demo-speech-text-chat/blob/main/diagram.png "Chatbot integration diagram")

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
