"""
Auto-BOT Application Package
Provides path utilities for both development and PyInstaller bundled execution.
"""

import os
import sys


def get_base_path():
    """
    Returns the base path for the application.
    - In development: Returns the project root directory
    - In PyInstaller bundle: Returns the _MEIPASS temporary directory
    """
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller bundle
        return sys._MEIPASS
    else:
        # Running in development
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_assets_path():
    """
    Returns the path to the assets directory.
    """
    return os.path.join(get_base_path(), 'assets')


def get_audio_path():
    """
    Returns the path to the audio assets directory.
    """
    return os.path.join(get_assets_path(), 'audio')


def get_audio_file(filename):
    """
    Returns the full path to a specific audio file.
    """
    return os.path.join(get_audio_path(), filename)


def get_runtime_audio_dir():
    """
    Returns a writable directory for runtime audio files (TTS output, etc.).
    Uses the user's temp directory to ensure write access in packaged mode.
    """
    import tempfile
    runtime_dir = os.path.join(tempfile.gettempdir(), 'AutoBOT_Audio')
    os.makedirs(runtime_dir, exist_ok=True)
    return runtime_dir


def get_runtime_audio_file(filename):
    """
    Returns the full path to a runtime audio file (writable location).
    """
    return os.path.join(get_runtime_audio_dir(), filename)


# Package version
__version__ = "1.0.0"
__app_name__ = "Auto-BOT"
