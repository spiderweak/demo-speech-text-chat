"""
text_processing.py

This module handles the processing of text using the Llama model. It includes functions and classes for text
refactoring, conversation management, and interaction with the Llama language model.
"""

import os
import logging
import threading
from .utils import load_text_model
from typing import Tuple

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
        output = llm(prompt, max_tokens=4096, echo=False)
        return output['choices'][0]['text'] # type:ignore
    except Exception as e:
        # Log the error and return an empty DataFrame or handle it as needed.
        logging.error(f"Unexpected error: {e}")

    return "Error in processing, sorry for the delay, please retry"


class Conversation:
    """Manages and processes a conversation using the Llama language model.

    This class handles the interaction flow of a chatbot conversation. It maintains the
    conversation history, processes incoming messages, and generates responses using the
    Llama model. The conversation begins with a predefined system message template, which
    sets the initial context or instructions for the interaction.

    Attributes:
        messages (list of dict): A list of messages in the conversation, where each message
                                 is a dictionary containing either a 'user' or 'system' key.
        conversation (str): A string representation of the entire conversation, including
                            both system and user messages.

    Methods:
        reception(message: str): Processes a received user message and updates the conversation.
        respond(): Generates a response using the Llama model based on the current conversation.
        generate_conversation(): Updates the conversation string based on accumulated messages.
    """

    def __init__(self) -> None:
        """Initialize the conversation with the system template.

        The conversation is started with a predefined system message template,
        which sets the context or instructions for the conversation.
        """

        self.messages = [{"system": DEFAULT_TEMPLATE}]
        self.conversation = self.messages[0]["system"]

    def reception(self, message: str):
        """Processes a received message and generates a response.

        This method appends the user's message to the conversation and then generates a response using the Llama model.

        Args:
            message (str): The message received from the user.

        Returns:
            str: The generated response from the chatbot.
        """
        if llm is None:
            return 400, "Model is not loaded yet, please retry in 2 minutes"

        prompt = USER_PROMPT.replace('{INSERT_PROMPT_HERE}', message)
        self.messages.append({"user": prompt})

        self.generate_conversation()

        return self.respond()


    def generate_conversation(self):
        """Generates the full conversation string from the accumulated messages."""

        self.conversation = "".join([list(message.values())[0] for message in self.messages])


    def respond(self) -> Tuple[int, str]:
        """Generates and handles the response from the chatbot.

        This function calls the Llama model with the current conversation and appends the model's response to the conversation.

        Returns:
            str: The response generated by the chatbot.
        """
        with model_ready_condition:
            while llm is None:
                model_ready_condition.wait()

        try:
            output = llm(self.conversation , max_tokens=2048, echo=False)
            answer_text = output['choices'][0]['text'] # type:ignore
            logging.info(f"\nCHATBOT ANSWER \n {answer_text}")
            self.messages.append({"system": answer_text})
            self.generate_conversation()

            return 200, answer_text

        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            return 400, "Unexpected error, please retry."


