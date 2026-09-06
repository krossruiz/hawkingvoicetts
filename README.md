# hawkingvoicetts

Chat with a local [Ollama](https://ollama.com) model and hear its replies spoken aloud — in Stephen Hawking's iconic robotic DECtalk-style voice, or one of twenty realistic neural voices. Runs entirely offline, no cloud APIs, no accounts.

## What it does

- Picks any locally-installed Ollama model and chats with it from the terminal.
- Speaks the model's replies (and optionally your own typed messages) using local TTS.
- Two voice engines:
  - **Hawking** — an eSpeak-NG configuration tuned to approximate the "Perfect Paul" DECtalk voice Stephen Hawking used.
  - **Piper** — realistic neural voices (a 10 women / 10 men roster; only the ones you've downloaded show up in the menu).
- Optional live translation: if your chat model replies in a different language than you want to hear, replies are auto-translated (sentence-by-sentence, with retries) before being spoken, using a second local Ollama model as the translator.
- Can save any reply to a `.wav` file.

## Requirements

- [Ollama](https://ollama.com) running locally (`ollama serve`), with at least one model pulled (e.g. `ollama pull llama3.2`).
- [eSpeak-NG](https://github.com/espeak-ng/espeak-ng) installed (for the Hawking voice): `winget install eSpeak-NG.eSpeak-NG`.
- Python 3.10+, with `requests`, `questionary`, and `piper-tts` installed.
- (Optional) Piper voice models downloaded into `./voices/` for realistic voices:
  ```
  python -m piper.download_voices --download-dir voices en_US-amy-medium en_US-ryan-medium
  ```

## Install

```
pip install -e .          # from a clone, editable
# or, once published:
pip install hawkingvoicetts
# conda:
conda install -c <your-channel> hawkingvoicetts
```

## Usage

```
hawkingvoicetts                                             # fully interactive
hawkingvoicetts --setup                                     # wizard: pick a model tier, get a recommendation
hawkingvoicetts --model llama3.2 --model-voice hawking --user-voice amy
hawkingvoicetts --model llama3.2 --model-voice hawking --prompt "Explain black holes"
hawkingvoicetts --no-speak-user                              # don't speak what you type, only replies

# still works via python -m, or the module directly:
python -m hawkingvoicetts.cli --model llama3.2
```

`--setup` asks how you want replies to feel (realtime / a short wait is fine / GPU has headroom), shows the matching model recommendations, then lets you pick from what you already have installed. It's a terminal wizard, not a GUI — no window toolkit is bundled with this package.

Key flags:

| Flag | Purpose |
|---|---|
| `--model` | Ollama model to chat with (skips the picker) |
| `--model-voice` / `--user-voice` | Voice id for the model's replies / your own messages |
| `--prompt` | One-shot mode instead of interactive chat |
| `--save-dir` | Save each reply as a `.wav` file |
| `--translate-to LANGUAGE` | Language to translate replies into before speaking |
| `--no-translate` | Disable auto-translation |
| `--translator-model` | Ollama model used for translation |

## Project layout

- `hawkingvoicetts/cli.py` — entry point: model/voice selection, chat loop, translation glue. Installed as the `hawkingvoicetts` command.
- `hawkingvoicetts/hawking_tts.py` — the eSpeak-NG-based Hawking voice.
- `hawkingvoicetts/tts_engine.py` — dispatches a chosen voice to either the Hawking engine or Piper.
- `hawkingvoicetts/voices_catalog.py` — the voice roster and interactive picker.
- `hawkingvoicetts/model_wizard.py` — the `--setup` model-recommendation wizard.
- `hawkingvoicetts/config.py` — settings file (`~/.hawkingvoicetts/config.json`) and language-detection helpers.

## Publishing

**PyPI:**
```
python -m pip install --upgrade build twine
python -m build                       # produces dist/*.whl and dist/*.tar.gz
twine upload dist/*                   # asks for your PyPI credentials/token
```

**conda:** build locally with the recipe in `conda-recipe/`, then upload to your own channel (e.g. an anaconda.org account) — this project isn't on conda-forge.
```
conda install conda-build anaconda-client
conda-build conda-recipe/
anaconda upload <path-to-built-package>
```

Both are inert until you actually run the upload step — nothing here publishes automatically.

## Status

Personal, local-first hobby project. No telemetry, no server component, no paid tier — everything runs on your own machine against your own Ollama install.

## License

None yet — see the note above about what that means for reuse. Add one (MIT is a reasonable default) before publishing to PyPI/conda if you want others to legally be able to use this.
