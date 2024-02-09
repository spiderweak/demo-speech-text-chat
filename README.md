# Démo Speech Text Chat

This project is a Flask web application that captures audio from the user's microphone and uses OpenAI's Whisper model for speech-to-text transcription.

This software is provided as is, without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose, and non-infringement. In no event shall the authors or copyright holders be liable for any claim, damages, or other liability, whether in an action of contract, tort, or otherwise, arising from, out of, or in connection with the software or the use or other dealings in the software.

## Features

- Record audio directly in the web browser.
- Send the audio data to a Flask server.
- Use Whisper to transcribe the audio to text.
- Display the transcription result on the web page.
- Real Time Transcription
- Working chatbot
- Streamed response
- Text-to-speech responses

# Todo

- Various feedback loops to improve the quality of the transcript as well as the questions/answers
- log conversations to central contexts in case further processing is needed

- Real time transcription improvements
- Chatbot improvement (user initial prompt handling)
- AOB

Also:
- Fix unsafe Wekzeug usage for production

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

What things you need to install the software and how to install them:

- python3
- pip

Also, for optional dependencies:

- virtualenv
- - ffmpeg (for the audio processing (both this project and openai-whisper))
- Docker (optional for containerization)

And for the audio outputs (dependencies from pyttsx3, see [Synthesizer support](https://pyttsx3.readthedocs.io/en/latest/support.html)):

- sapi5 (Windows)
- nsss (Mac OS)
- espeak (Linux)


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

The container does not copy chat models locally, but you can mount the models in a dedicated folder if you want to use your own model. Just don't forget to change the environment variables defined in the .env file:

```bash
docker run -p 5000:5000 -v $(pwd)/app/models:/app/models demo-speech-text-chat
```

## Interfaces diagram

![Chatbot integration diagram](diagram.jpg) "Chatbot integration diagram"

## Contributing

This project does not accept exterior contributions for now.

## Authors

Antoine ["Spiderweak"](https://github.com/spiderweak) BERNARD

## License

Unless part of the system is incompatible with it, consider this project under CC BY-NC-SA and mostly used for research purposes and teaching.

## Acknowledgments

Thanks to these project, that make most of the project run
- OpenAI for the Whisper model and for the disclaimer in the opening statement of this README.
- Flask
