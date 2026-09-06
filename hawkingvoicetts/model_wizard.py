"""
Startup wizard: a short back-and-forth that picks a sensible Ollama model
and voice for you, instead of making you already know the roster.

Terminal only. A GUI version is real extra surface (window toolkit, packaging,
event loop) that wasn't built here — this covers the "ask a couple questions,
get a recommendation" need without pretending to ship a GUI that doesn't exist.
"""

from __future__ import annotations

import questionary

# Same three tiers shown on the project landing page: how fast you need a
# reply vs. how much GPU you're willing to dedicate to getting it.
MODEL_TIERS = {
    "realtime": {
        "label": "Realtime replies (voice chat, want it to feel instant)",
        "models": ["qwen2.5:3b-instruct", "llama3.2:3b", "phi3.5:3.8b"],
        "note": "Small enough to answer in well under a second on most GPUs, "
                "or a few seconds on CPU-only.",
    },
    "timed": {
        "label": "Semi-automatic / timed (a short wait per reply is fine)",
        "models": ["llama3.1:8b-instruct", "qwen2.5:7b-instruct", "mistral:7b-instruct"],
        "note": "Noticeably better reasoning and phrasing than the 3B tier, "
                "at the cost of a several-second wait per reply.",
    },
    "gpu": {
        "label": "Best quality, GPU has the headroom (24GB+ VRAM)",
        "models": ["llama3.1:70b-instruct-q4_0", "qwen2.5:32b-instruct", "mixtral:8x7b-instruct"],
        "note": "Needs real GPU memory to stay fast; on CPU-only these are slow.",
    },
}


def _has_nvidia_gpu() -> bool:
    try:
        import subprocess
        subprocess.run(
            ["nvidia-smi"], capture_output=True, timeout=3, check=True,
        )
        return True
    except Exception:
        return False


def run_wizard(installed_models: list[str]) -> tuple[str, str]:
    """Ask a few questions, return (chosen_model, translator_model).

    `installed_models` is what's already pulled in Ollama; recommendations
    that aren't installed are shown with a note so the user can `ollama pull`
    them, but the picker only lets you choose one you already have.
    """
    gpu = _has_nvidia_gpu()
    print(f"[wizard] NVIDIA GPU detected: {'yes' if gpu else 'no'}\n")

    tier_key = questionary.select(
        "What do you want out of replies?",
        choices=[questionary.Choice(title=v["label"], value=k) for k, v in MODEL_TIERS.items()],
    ).ask()
    if tier_key is None:
        raise SystemExit("Cancelled.")

    tier = MODEL_TIERS[tier_key]
    print(f"\n{tier['note']}")
    print("Recommended models for this tier: " + ", ".join(tier["models"]) + "\n")

    available = [m for m in tier["models"] if any(m.split(":")[0] in im for im in installed_models)]
    candidates = available or installed_models
    if not candidates:
        raise SystemExit(
            "None of the recommended models are installed yet. Pull one first, e.g.:\n"
            f"  ollama pull {tier['models'][0]}"
        )

    model = questionary.select(
        "Which installed model should handle the chat?",
        choices=candidates,
        default=candidates[0],
    ).ask()
    if model is None:
        raise SystemExit("Cancelled.")

    small_models = [m for m in installed_models if any(t in m for t in ("3b", "1b", "phi3"))]
    translator_default = small_models[0] if small_models else (installed_models[0] if installed_models else model)
    translator = questionary.select(
        "Which model should do live translation (a small, fast one works best)?",
        choices=installed_models,
        default=translator_default,
    ).ask()
    if translator is None:
        raise SystemExit("Cancelled.")

    return model, translator
