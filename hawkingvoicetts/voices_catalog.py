"""
Catalog of available TTS voices for the Ollama voice wrapper.

Two kinds of voice:
  - "hawking": routed to hawking_tts.py (eSpeak-NG, robotic DECtalk-style voice)
  - "piper":   routed to a local Piper neural TTS model (realistic voice)

The full target roster is 10 realistic women + 10 realistic men (see
PIPER_ROSTER below), but a voice only shows up in the menu once its model
files actually exist in ./voices/. Download missing ones with:

    python -m piper.download_voices --download-dir voices <voice-name>

e.g. to fill out the roster later:
    python -m piper.download_voices --download-dir voices en_US-bryce-medium en_US-danny-low \
        en_US-hfc_male-medium en_US-joe-medium en_US-john-medium en_US-kusal-medium \
        en_US-norman-medium en_US-ryan-medium en_US-sam-medium en_GB-alan-medium \
        en_GB-cori-medium en_GB-jenny_dioco-medium en_GB-southern_english_female-low
"""

import os
import sys
from dataclasses import dataclass

import questionary

VOICES_DIR = "voices"

# label + gender for every voice in the intended 10+10 roster; only ones
# whose .onnx file is present in VOICES_DIR actually appear in the menu.
PIPER_ROSTER = {
    "en_US-amy-medium": ("Amy (US)", "female"),
    "en_US-hfc_female-medium": ("Hannah (US)", "female"),
    "en_US-kathleen-low": ("Kathleen (US)", "female"),
    "en_US-kristin-medium": ("Kristin (US)", "female"),
    "en_US-lessac-medium": ("Lessac (US)", "female"),
    "en_US-ljspeech-medium": ("Eliza (US)", "female"),
    "en_GB-alba-medium": ("Alba (UK)", "female"),
    "en_GB-cori-medium": ("Cori (UK)", "female"),
    "en_GB-jenny_dioco-medium": ("Jenny (UK)", "female"),
    "en_GB-southern_english_female-low": ("Southern English Female (UK)", "female"),

    "en_US-bryce-medium": ("Bryce (US)", "male"),
    "en_US-danny-low": ("Danny (US)", "male"),
    "en_US-hfc_male-medium": ("Henry (US)", "male"),
    "en_US-joe-medium": ("Joe (US)", "male"),
    "en_US-john-medium": ("John (US)", "male"),
    "en_US-kusal-medium": ("Kusal (US)", "male"),
    "en_US-norman-medium": ("Norman (US)", "male"),
    "en_US-ryan-medium": ("Ryan (US)", "male"),
    "en_US-sam-medium": ("Sam (US)", "male"),
    "en_GB-alan-medium": ("Alan (UK)", "male"),
}


@dataclass(frozen=True)
class Voice:
    id: str
    label: str
    gender: str        # "robotic", "female", "male"
    engine: str         # "hawking" or "piper"
    piper_model: str | None = None  # piper voice name, e.g. "en_US-amy-medium"


def _discover_piper_voices() -> list[Voice]:
    found = []
    for model_name, (label, gender) in PIPER_ROSTER.items():
        onnx_path = os.path.join(VOICES_DIR, f"{model_name}.onnx")
        if os.path.isfile(onnx_path):
            found.append(Voice(model_name, label, gender, "piper", model_name))
    return found


def load_voices() -> list["Voice"]:
    voices = [Voice("hawking", "Hawking (robotic synthesizer)", "robotic", "hawking")]
    voices.extend(_discover_piper_voices())
    return voices


VOICES: list[Voice] = load_voices()
VOICES_BY_ID = {v.id: v for v in VOICES}

_missing_count = len(PIPER_ROSTER) - (len(VOICES) - 1)
if _missing_count:
    print(
        f"[voices_catalog] {_missing_count} of {len(PIPER_ROSTER)} roster voices not yet "
        f"downloaded (missing .onnx files in ./{VOICES_DIR}/) — they won't appear in the menu."
    )


def piper_model_path(voice: Voice) -> str:
    return os.path.join(VOICES_DIR, f"{voice.piper_model}.onnx")


def choose_voice(prompt: str) -> Voice:
    order = {"robotic": 0, "female": 1, "male": 2}
    section_label = {"robotic": "-- Robotic --", "female": "-- Women --", "male": "-- Men --"}
    choices = []
    last_gender = None
    for v in sorted(VOICES, key=lambda v: (order[v.gender], v.label)):
        if v.gender != last_gender:
            choices.append(questionary.Separator(section_label[v.gender]))
            last_gender = v.gender
        choices.append(questionary.Choice(title=v.label, value=v.id))

    answer = questionary.select(prompt, choices=choices).ask()
    if answer is None:
        sys.exit("Cancelled.")
    return VOICES_BY_ID[answer]
