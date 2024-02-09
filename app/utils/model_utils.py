import os
import requests
import logging

from dotenv import load_dotenv
from llama_cpp import Llama

load_dotenv()

def load_text_model(model_path = None, model_url : str = "https://huggingface.co/TheBloke/zephyr-7B-beta-GGUF/resolve/main/zephyr-7b-beta.Q6_K.gguf"):
    """
    Load the Llama model, downloading it from a specified URL if it's not already present locally.

    This function attempts to load a Llama model from a specified path. If the model is not found,
    it downloads the model from a specified URL or a default URL. The function checks for the
    presence of a model at 'model_path'. If not found, it attempts to download the model from
    'model_url'.

    Args:
        model_path (str, optional): The local file system path where the model is stored or will be saved.
                                    If not provided, the function tries to retrieve it from the
                                    'LLAMA_MODEL_PATH' environment variable.
        model_url (str, optional): The URL to download the model if it's not present at 'model_path'.
                         Defaults to a specific model URL on Hugging Face. This parameter is
                         overridden by the 'LLAMA_MODEL_URL' environment variable if it's set.

    Returns:
        Llama: An instance of the Llama model loaded from 'model_path'.

    Raises:
        EnvironmentError: If 'model_path' is not provided and the 'LLAMA_MODEL_PATH' environment
                          variable is not set or if the model cannot be found and fails to download.
        Exception: If the model download fails due to network issues or other errors indicated by
                   a non-200 HTTP status code.
        ValueError: If the Llama model initialization fails due to invalid parameters or other issues.

    Note:
        It is recommended to set 'LLAMA_MODEL_PATH' and 'LLAMA_MODEL_URL' environment variables
        for flexibility and to avoid hardcoded paths, even if the code works around it if necessary.
    """

    model_path = os.getenv("LLAMA_MODEL_PATH") or model_path

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
        # TODO : These need to be modified, loaded from a config class ?
        llm = Llama(model_path=model_path, n_ctx=40960, n_batch=128, verbose=False)
        return llm
    except ValueError as ve:
        logging.error(ve)
        raise
