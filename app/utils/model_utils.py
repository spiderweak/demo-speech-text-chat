import os
import requests
import logging

from dotenv import load_dotenv
from llama_cpp import Llama

def load_text_model(model_path = None, model_url = "https://huggingface.co/TheBloke/zephyr-7B-beta-GGUF/resolve/main/zephyr-7b-beta.Q6_K.gguf"):
    """Load the model, downloading it if it's not already present."""
    load_dotenv()

    model_path = os.getenv("LLAMA_MODEL_PATH")

    if model_path is None:
        raise EnvironmentError(f"LLAMA_MODEL_PATH environment variable not set")

    if not os.path.exists(model_path):
        model_url = os.getenv("LLAMA_MODEL_URL") or model_url
        logging.warning(f"Model not found at {model_path}, downloading from {model_url}...")

        response = requests.get(model_url)

        if response.status_code == 200:
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            with open(model_path, 'wb') as model_file:
                model_file.write(response.content)
        else:
            raise Exception(f"Failed to download model. HTTP status code: {response.status_code}")
    else:
        logging.debug(f"Model found at {model_path}, loading...")

    try:
        llm = Llama(model_path=model_path, n_ctx=40960, n_batch=128, verbose=False)
        return llm
    except ValueError as ve:
        logging.error(ve)
        raise
