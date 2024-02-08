"""
text_processing.py

This module handles the processing of text using the Llama model. It includes functions and classes for text
refactoring, conversation management, and interaction with the Llama language model.
"""

import logging
import threading
import tempfile
import uuid
import re
import base64
import os

from .utils.utils import load_text_model, TextToSpeechConverter
from typing import Tuple, Optional
from .socket_routes import socketio

# We're loading the model at the beginning,
# it would probably be better to work another way


# Initialize a condition variable
model_ready_condition = threading.Condition()
llm = None

def load_model_in_background():
    global llm
    logging.info("Loading model in background, this might take a while")
    with model_ready_condition:
        llm = load_text_model()
        model_ready_condition.notify_all()  # Notify all waiting threads that model is ready

# Load model in a separate thread
model_loading_thread = threading.Thread(target=load_model_in_background)
model_loading_thread.start()


DEFAULT_TEMPLATE="""
[INST] <|system|>
You are CHRONOS Chat, a helpful, respectful and honest chatbot interface.

You are running on CPU-only devicess from the company Humanitas,
a startup based in Montreal and lead by Abdo Shabah, for demonstration purpose.

This chat interface aims to assist managers and employees
so that they save time working on repetitive tasks,
such as filling up forms, generating workflows, or gathering
information from multiple sources.

As part of this demo, you will be asked some generic questions.
Please keep your answer short, under 200 characters if possible.
Some questions might be asked in a different language than English,
in that case, please answer in the same language the question was asked.
</s>
"""

USER_PROMPT ="""
<|user|>
{INSERT_PROMPT_HERE} </s>

<|assistant|>
"""

def refactor_input(text:str) -> str:
    """Processes the given text to correct any transcription errors using the Llama model.

    The function applies a template to the text for the Llama model to interpret and correct. The template
    instructs the model to focus on correcting spelling, grammar, and other errors.

    Args:
        text (str): The text to be processed and corrected.

    Returns:
        str: The corrected text as processed by the Llama model.

    Note:
        - TODO: Improve the template as the current responses may not be satisfactory.
        - TODO: Implement more specific error handling related to Llama model interactions.
    """

    template = """
    [INST] <|system|>
    You are a helpful, respectful and honest assistant.
    Always answer as helpfully as possible, while being safe.

    You will be given a text, transcribed from an automatic
    transcription software. You are tasked to correct enventual
    mistakes in spelling, grammar or any other things in order to
    provide the best quality transcription possible.

    Please, only answer with the corrected text as your answer will
    processed automatically. It is important for us to have the best
    text quality possible.
    </s>

    <|user|> Here is the text to review:
    {INSERT_PROMPT_HERE} </s>

    <|assistant|>
    """

    prompt = template.replace('{INSERT_PROMPT_HERE}', text)

    try:
        output = llm(prompt, max_tokens=4096, echo=False) # type:ignore
        return output['choices'][0]['text'] # type:ignore
    except Exception as e:
        # Log the error and return an empty DataFrame or handle it as needed.
        logging.error(f"Unexpected error: {e}")

    return "Error in processing, sorry for the delay, please retry"

class Message:
    def __init__(self, emitter: str, content: str = "") -> None:
        self.id = uuid.uuid4()
        self.emitter = emitter
        self.content = content

    @property
    def emitter(self):
        return self._emitter

    @emitter.setter
    def emitter(self, emitter):
        self._emitter = emitter

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, content):
        self._content = content


class Conversation:
    """Manages and processes a conversation using the Llama language model.

    This class handles the interaction flow of a chatbot conversation. It maintains the
    conversation history, processes incoming messages, and generates responses using the
    Llama model. The conversation begins with a predefined system message template, which
    sets the initial context or instructions for the interaction.

    Attributes:
        messages (list of Message): A list of messages in the conversation, where each message
                                 is a dictionary containing either a 'user' or 'system' key.
        conversation (str): A string representation of the entire conversation, including
                            both system and user messages.

    Methods:
        reception(message: str): Processes a received user message and updates the conversation.
        respond(): Generates a response using the Llama model based on the current conversation.
        generate_conversation(): Updates the conversation string based on accumulated messages.
    """

    def __init__(self, temp_folder: Optional[tempfile.TemporaryDirectory] = None, session_id : Optional[str] = None) -> None:
        """Initialize the conversation with the system template.

        The conversation is started with a predefined system message template,
        which sets the context or instructions for the conversation.
        """

        init_message = Message("system", DEFAULT_TEMPLATE)

        self.messages = [init_message]
        self.conversation = self.messages[0].content

        self.session_id = session_id
        self._temp_folder = temp_folder or tempfile.TemporaryDirectory()
        self.temp_folder_name = self._temp_folder.name

        self.tts_interface = None

    def reception(self, message: str):
        """Processes a received message and generates a response.

        This method appends the user's message to the conversation and then generates a response using the Llama model.

        Args:
            message (str): The message received from the user.

        Returns:
            int: The response code
            Message: The generated response from the chatbot.
        """
        if llm is None:
            error = Message("error", "Model is not loaded yet, please retry in 2 minutes")
            return 400, error

        prompt = USER_PROMPT.replace('{INSERT_PROMPT_HERE}', message)
        new_message = Message("user", prompt)
        self.messages.append(new_message)

        self.generate_conversation()

        return self.respond()


    def generate_conversation(self):
        """Generates the full conversation string from the accumulated messages."""
        self.conversation = "".join(message.content for message in self.messages)


    def respond(self) -> Tuple[int, Message]:
        """Generates and handles the response from the chatbot.

        This function calls the Llama model with the current conversation and appends the model's response to the conversation.

        Returns:
            int: The response code
            Message: The response generated by the chatbot.
        """
        with model_ready_condition:
            while llm is None:
                model_ready_condition.wait()

        speech_message = ""
        try:
            output = llm(self.conversation, max_tokens=2048, echo=False, stream=True)
            new_message = Message("system")
            for item in output:
                chunck = item['choices'][0]['text'] # type:ignore
                logging.debug(f"\nCHATBOT CHUNK \n {chunck}")
                self.stream_answer(new_message.id, chunck)
                new_message.content += chunck
                speech_message += chunck
                if bool(re.search(r"[!.:;?]", chunck)):
                    self.talk_answer(speech_message)
                    logging.info(f"\nTTS CHUNK \n {speech_message}")
                    speech_message = ""


            self.messages.append(new_message)
            self.generate_conversation()

            logging.info(f"\nCHATBOT ANSWER \n {new_message.content}")

            response = Message("debug", "Message processing success")

            return 200, response

        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            error = Message("error", "Unexpected error, please retry.")
            return 400, error

    def stream_answer(self, message_id, chunk):
        try:
            # Constructing a response object, could be JSON or other format
            response = {
                "message_id": str(message_id),
                "sender" : "system",
                "content": chunk
            }
            logging.debug(f"Sending data on channel 'stream_message' to {self.session_id} with response: {response}")
            # Emit the response chunk to the client
            socketio.emit('stream_message', response, to=self.session_id)  # 'chat_response' is the event name
        except Exception as e:
            logging.error(f"Error while streaming response: {e}")

    def talk_answer(self, sentence):
        try:
            self.tts_interface = TextToSpeechConverter()
            base64_audio = self.tts_interface.convert_text_to_speech(sentence, self.temp_folder_name)
            socketio.emit('speech_file', {'audio': base64_audio}, to=self.session_id)
            del self.tts_interface
        except Exception as e:
            logging.error(f"Audio error : {e}")
