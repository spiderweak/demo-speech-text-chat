class TimeoutError(Exception):
    """Exception raised when a thread operation exceeds the allowed time."""
    pass

class MissingPackageError(Exception):
    """Exception raised when missing a package, only checked with ffmpeg for now."""
    pass

class TextToSpeechTimeoutError(Exception):
    """Exception raised when text-to-speech conversion exceeds the allowed time."""
    pass