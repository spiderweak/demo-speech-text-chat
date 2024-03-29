import subprocess
import logging

def check_ffmpeg_installed():
    """Check if ffmpeg is installed on the system."""
    try:
        # Run 'ffmpeg -version' command and capture its output
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except subprocess.CalledProcessError as e:
        logging.error("ffmpeg is not installed or not in PATH.")
        return False
    except FileNotFoundError:
        logging.error("ffmpeg command not found.")
        return False


def convert_audio_data(origin, destination):
    try:
        subprocess.run(["ffmpeg", '-i', origin, '-ac', '2', destination ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except subprocess.CalledProcessError as e:
        logging.error("ffmpeg Error during conversion")
        return False
    except FileNotFoundError:
        logging.error("ffmpeg command not found.")
        return False
