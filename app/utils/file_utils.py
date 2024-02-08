import logging
import os
from datetime import datetime

def generate_audioblob_filename(folder_name: str) -> str:
    """Generate a filename for an audio blob using the current date and time.

    This function creates a filename with a timestamp format based on the current date and time,
    ensuring uniqueness for each file. The filename will have a '.webm' extension, which can be
    replaced with an appropriate extension if necessary.

    Args:
        folder_name (str): The name of the folder where the audio blob will be saved.

    Returns:
        str: The generated filename, which includes the folder path, a timestamp, and the '.webm' extension.
    """

    filename_date = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(folder_name, f"{filename_date}.webm")

    return filename



def save_data_to_file(data: bytes, filename: str):
    """Save data to a file.

    Args:
        data (bytes): The audio data to save.
        filename (str): The filename where the data should be saved.
    """

    with open(filename, 'wb') as file:
        file.write(data)
        logging.debug(f"(Audio) data saved as {filename}")

