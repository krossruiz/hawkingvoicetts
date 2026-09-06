"""
Local config + small language helpers shared by the CLI: where the
translator's per-user settings live, and language detection/cleanup used
before text is spoken.

Vendored from the sibling ollamamodeltranslator project so this package has
no dependency outside itself and can be installed standalone via pip/conda.
"""

import json
import os
import re
import sys

CONFIG_PATH = os.path.join(
    os.path.expanduser("~"), ".hawkingvoicetts", "config.json"
)

DEFAULTS = {
    "translator_model": "qwen2.5:7b-instruct",
    "user_language": "English",
}

THINK_RE = re.compile(r"<think>.*?</think>\s*", re.DOTALL | re.IGNORECASE)
CJK_RE = re.compile(r"[぀-ヿ㐀-䶿一-鿿豈-﫿ｦ-ﾟ]")


def strip_think(text: str) -> str:
    return THINK_RE.sub("", text).strip()


def load_config() -> dict:
    cfg = dict(DEFAULTS)
    cfg["model_languages"] = {}
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, encoding="utf-8") as f:
                cfg.update(json.load(f))
        except (OSError, json.JSONDecodeError) as e:
            print(f"Warning: could not read {CONFIG_PATH}: {e}", file=sys.stderr)
    return cfg


def save_config(cfg: dict) -> None:
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
    except OSError as e:
        print(f"Warning: could not save config: {e}", file=sys.stderr)


def detect_language(text: str, translator_model: str, chat_fn) -> str | None:
    """Best-effort language name for a chunk of text. `chat_fn(model, messages) -> str`."""
    messages = [
        {
            "role": "system",
            "content": "Identify the language of the user's text. "
            "Reply with only the English name of the language, one word.",
        },
        {"role": "user", "content": text[:800]},
    ]
    try:
        out = strip_think(chat_fn(translator_model, messages))
    except Exception:
        return None
    out = out.strip().strip(".").splitlines()[0].strip()
    return out if out and len(out) < 30 else None
