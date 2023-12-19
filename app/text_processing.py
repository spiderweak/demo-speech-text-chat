from dotenv import load_dotenv
from llama_cpp import Llama
import logging
import os


# We're loading the model at the beginning,
# it would probably be better to work another way
# (also, it's noisy in the python console)

load_dotenv()
text_model_path = os.getenv("LLAMA_MODEL_PATH")
llm = Llama(model_path=text_model_path, n_ctx=40960, n_batch=128, verbose=False)

def refactor_input(text:str):
    """
        TODO: Improve the template as the answer is not satisfying for now
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

    # Better error handling would be necessary here:
    # TODO: Better error handling
    try:
        output = llm(prompt, max_tokens=4096, echo=False)
        answer_text = output['choices'][0]['text']
        logging.info(f"{answer_text}")
    except Exception as e:
        # Log the error and return an empty DataFrame or handle it as needed.
        logging.error(f"Error when calling model: {e}")
        answer_text = "Error in processing, sorry for the delay, please retry"

    return answer_text


DEFAULT_TEMPLATE="""
[INST] <|system|>
You are CHRONOS Chat, a helpful, respectful and honest chatbot interface.

You are running on CPU-only devicess from the company Humanitas,
a startup based in Montreal and lead by Abdo Shabah, for demonstration purpose.
</s
"""
"""
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

class Conversation:

    def __init__(self) -> None:
        """
            Initialize the conversation with the system template
        """
        self.messages = [{"system": DEFAULT_TEMPLATE}]
        self.conversation = self.messages[0]["system"]


    def init_message(self, first_message = "<|user|> </s>"):
        """
            First message will be from the speech-to-text interface
        """
        self.message = USER_PROMPT

        prompt = self.message.replace('{INSERT_PROMPT_HERE}', first_message)
        self.messages.append({"user":prompt})

        output = [list(message.values())[0] for message in self.messages]
        self.conversation = "".join(output)

        # Also, might be good to have a way to link the message to
        # content in the conversation on screen to allow from user-side
        # personalization and bugfixes


    def respond(self):
        """
            This function generates and handles the response from the chatbot
            TODO : Review this try-except part to handle the errors more properly
        """

        try:
            output = llm(self.conversation , max_tokens=2048, echo=False)
            answer_text = output['choices'][0]['text']
            self.messages.append({"system": answer_text})
            self.conversation = "".join([list(message.values())[0] for message in self.messages])
            logging.info(f"{answer_text}")
        except Exception as e:
            # Log the error and return an empty DataFrame or handle it as needed.
            logging.error(f"Error when calling model: {e}")
            answer_text = "Error in processing, sorry for the delay, please retry"
        return answer_text


    def reception(self, message):
        """
            What to do on message reception
            TODO:
            - Move the conversation generator to another function
            - Remove the self.respond at the end, a cleaner solution will me necessary
        """

        prompt = USER_PROMPT.replace('{INSERT_PROMPT_HERE}', message)

        self.messages.append({"user":prompt})

        self.conversation = "".join(list(message.values())[0] for message in self.messages)
        output = self.respond()
        return output
