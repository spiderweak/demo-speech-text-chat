import logging
import os
from datetime import datetime


def generate_filename(folder_name: str, extension: str = 'webm') -> str:
    """Generate a unique filename using the current date and time.

    This function creates a filename with a timestamp format based on the current date and time,
    ensuring uniqueness for each file. The filename will have a '.webm' extension by default,
    but can be replaced with another extension if necessary.

    Args:
        folder_name (str): The name of the folder where the file will be saved.
        extension (str): The file extension to use. Defaults to 'webm'.

    Returns:
        str: The generated filename, which includes the folder path, a timestamp, and the specified extension.

    Raises:
        ValueError: If the folder_name is empty.
    """
    if not folder_name:
        raise ValueError("Folder name cannot be empty.")

    filename_date = datetime.now().strftime("%Y%m%d_%H%M%S")

    if extension:
        filename = os.path.join(folder_name, f"{filename_date}.{extension}")
    else:
        filename = os.path.join(folder_name, f"{filename_date}")

    return filename


def save_data_to_file(data: bytes, filename: str):
    """Save data to a file.

    Args:
        data (bytes): The audio data to save.
        filename (str): The filename where the data should be saved.

    Raises:
        ValueError: If the data is empty.
        IOError: If there's an issue writing to the file.
    """
    if not data:
        logging.error("Attempted to save empty data to a file.")
        raise ValueError("Data to save cannot be empty.")

    try:
        with open(filename, 'wb') as file:
            file.write(data)
            logging.debug(f"Data saved as {filename}")
    except IOError as e:
        logging.error(f"Failed to save data to {filename}: {e}")
        raise
