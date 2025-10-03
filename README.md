# ltts

Quick CLI for text-to-speech using Kokoro TTS. Runs locally on your machine.

## Install

```bash
pip install ltts
```

Or with uv:

```bash
uv tool install ltts
```

Or run directly without installing:

```bash
uvx ltts "hello world"
```

For development:

```bash
uv sync
```

## Usage

```bash
# Basic usage (outputs to output.mp3)
ltts "hello world"

# Specify output file
ltts "your text here" -o speech.mp3

# Different formats supported
ltts "test" -o output.ogg   # OGG
ltts "test" -o output.flac  # FLAC
ltts "test" -o output.wav   # WAV

# Use different voice
ltts "custom voice" -v am_adam    # Male American English
ltts "bonjour" -v ff_siwis        # French
ltts "こんにちは" -v jf_alpha      # Japanese

# Specify language code manually
ltts "こんにちは" -v jf_alpha -l j  # Japanese with explicit lang code

# Play audio through speakers instead of writing a file (ignores -o/--output)
ltts "Hello world" --say

# Read text from stdin (pipe)
echo "Hello from pipe" | ltts --say
cat notes.txt | ltts -o notes.mp3

# See all available voices
ltts --help
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
- **Japanese voices**: First use automatically downloads the Japanese dictionary (~526MB one-time download)
- Supports MP3, OGG, FLAC, and WAV output formats
- Language code is auto-detected from voice prefix (or use `-l` to specify manually)
- `--say` notes:
  - Requires `sounddevice` (installed via `uv sync` or as a dependency).
  - Plays at 24 kHz on the default output device.
  - On Linux, ensure your user can access audio (PulseAudio/PipeWire running).
  - On macOS, you may see a permissions prompt for audio.
