# tts

Quick CLI for text-to-speech using Kokoro TTS.

## Install

```bash
uv sync
```

## Usage

```bash
# Basic usage (outputs to output.mp3)
uv run tts "hello world"

# Specify output file
uv run tts "your text here" -o speech.mp3

# Different formats supported
uv run tts "test" -o output.ogg   # OGG
uv run tts "test" -o output.flac  # FLAC
uv run tts "test" -o output.wav   # WAV

# Use different voice
uv run tts "custom voice" -v am_adam    # Male American English
uv run tts "bonjour" -v ff_siwis        # French
uv run tts "こんにちは" -v jf_alpha      # Japanese

# See all available voices
uv run tts --help
```

## Available Voices

Kokoro supports 50+ voices across multiple languages:

- **American English**: af_heart, af_alloy, af_bella, af_nova, af_sarah, am_adam, am_michael, and more
- **British English**: bf_alice, bf_emma, bf_isabella, bm_daniel, bm_george
- **Japanese**: jf_alpha, jm_kumo
- **Chinese**: zf_xiaobei, zm_yunxi
- **Spanish**: ef_dora, em_alex
- **French**: ff_siwis
- **Hindi**: hf_alpha, hm_omega
- **Italian**: if_sara, im_nicola
- **Portuguese**: pf_dora, pm_alex

Full voice list: https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md

## Notes

- First run downloads the model (~330MB) to `~/.cache/huggingface/`
- Supports MP3, OGG, FLAC, and WAV output formats
- Pure Python, no external dependencies
