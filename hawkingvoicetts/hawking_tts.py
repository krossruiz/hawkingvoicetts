#!/usr/bin/env python3
"""
Local TTS in the style of Stephen Hawking's speech synthesizer.

Hawking used a hardware DECtalk unit (the "Perfect Paul" voice) starting in
the mid-1980s. That voice is a generic robotic formant synthesizer, not a
biometric recording of his own voice. This script approximates that
distinctive flat, low-pitched, metallic cadence using eSpeak-NG, which runs
entirely offline/locally.

Usage:
    python hawking_tts.py "Text to speak"
    python hawking_tts.py --save out.wav "Text to speak"
    python hawking_tts.py --interactive
"""

import argparse
import shutil
import subprocess
import sys
import tempfile
import os

# Tuned to approximate DECtalk "Perfect Paul": low flat pitch, measured pace,
# minimal pitch range, slightly nasal formant voice.
VOICE = "en-us"
PITCH = 20        # 0-99, lower = deeper/flatter (DECtalk was quite low & monotone)
SPEED = 150        # words per minute (Hawking's setting was ~130-160 wpm)
AMPLITUDE = 100    # volume 0-200


def find_espeak() -> str:
    exe = shutil.which("espeak-ng") or shutil.which("espeak")
    if exe:
        return exe
    common_paths = [
        r"C:\Program Files\eSpeak NG\espeak-ng.exe",
        r"C:\Program Files (x86)\eSpeak NG\espeak-ng.exe",
    ]
    for p in common_paths:
        if os.path.isfile(p):
            return p
    sys.exit(
        "espeak-ng not found. Install it (e.g. `winget install eSpeak-NG.eSpeak-NG`) "
        "and re-run."
    )


def build_command(espeak_path: str, text: str, out_file: str | None) -> list[str]:
    # Robotic flatness comes mainly from low pitch (-p) and word-gap (-g);
    # eSpeak-NG has no separate pitch-range flag.
    cmd = [
        espeak_path,
        "-v", VOICE,
        "-p", str(PITCH),
        "-s", str(SPEED),
        "-a", str(AMPLITUDE),
        "-g", "6",       # word gap in 10ms units -> slight pause between words
    ]
    if out_file:
        cmd += ["-w", out_file]
    cmd.append(text)
    return cmd


def speak(text: str, out_file: str | None = None):
    espeak_path = find_espeak()
    cmd = build_command(espeak_path, text, out_file)
    subprocess.run(cmd, check=True)


def main():
    parser = argparse.ArgumentParser(description="Local robotic TTS (Hawking-style synthesizer voice)")
    parser.add_argument("text", nargs="?", help="Text to speak")
    parser.add_argument("--save", metavar="FILE.wav", help="Save audio to a WAV file instead of/along with playing it")
    parser.add_argument("--interactive", action="store_true", help="Enter interactive mode: type lines to speak, Ctrl+C to quit")
    args = parser.parse_args()

    if args.interactive:
        print("Hawking-voice TTS — interactive mode. Type text and press Enter. Ctrl+C to exit.")
        try:
            while True:
                line = input("> ")
                if line.strip():
                    speak(line)
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye.")
        return

    if not args.text:
        parser.error("Provide text to speak, or use --interactive")

    speak(args.text, args.save)
    if args.save:
        print(f"Saved audio to {args.save}")


if __name__ == "__main__":
    main()
