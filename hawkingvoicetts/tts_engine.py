"""
Unified local TTS dispatch: routes a Voice (see voices_catalog.py) to either
eSpeak-NG (Hawking robotic voice) or a local Piper neural model (realistic
voices), and plays or saves the resulting audio.
"""

import os
import subprocess
import sys
import tempfile
import wave

from .voices_catalog import Voice, piper_model_path
from . import hawking_tts

_piper_voices_cache: dict[str, "PiperVoice"] = {}


def _get_piper_voice(model_path: str):
    from piper import PiperVoice

    if model_path not in _piper_voices_cache:
        if not os.path.isfile(model_path):
            sys.exit(
                f"Piper voice model not found: {model_path}\n"
                f"Download it with: python -m piper.download_voices --download-dir voices <voice-name>"
            )
        _piper_voices_cache[model_path] = PiperVoice.load(model_path)
    return _piper_voices_cache[model_path]


def _play_wav(path: str):
    if sys.platform == "win32":
        import winsound
        winsound.PlaySound(path, winsound.SND_FILENAME)
    else:
        subprocess.run(["aplay", path], check=False)


def speak(text: str, voice: Voice, out_file: str | None = None):
    """Speak `text` with the given Voice. If out_file is given, save (and don't necessarily play)."""
    if voice.engine == "hawking":
        hawking_tts.speak(text, out_file)
        return

    if voice.engine == "piper":
        model_path = piper_model_path(voice)
        piper_voice = _get_piper_voice(model_path)

        save_path = out_file
        temp_used = False
        if save_path is None:
            fd, save_path = tempfile.mkstemp(suffix=".wav")
            os.close(fd)
            temp_used = True

        with wave.open(save_path, "wb") as wav_file:
            piper_voice.synthesize_wav(text, wav_file)

        _play_wav(save_path)

        if temp_used:
            os.remove(save_path)
        return

    raise ValueError(f"Unknown engine: {voice.engine}")
