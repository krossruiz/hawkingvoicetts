"""hawkingvoicetts: local Ollama chat spoken aloud in a robotic or realistic voice."""

from .tts_engine import speak
from .voices_catalog import VOICES, VOICES_BY_ID, Voice, choose_voice

__version__ = "0.1.0"
__all__ = ["speak", "VOICES", "VOICES_BY_ID", "Voice", "choose_voice"]
