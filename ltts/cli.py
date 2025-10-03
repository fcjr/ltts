import os
import platform
import warnings
import argparse
import sys
from pathlib import Path
import numpy as np

# Enable MPS fallback on macOS
if platform.system() == 'Darwin':
    os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'

# Suppress specific noisy warnings early, before heavy imports
# PyTorch-specific noise
warnings.filterwarnings('ignore', category=UserWarning, module=r'^torch\.nn\.modules\.rnn$')
warnings.filterwarnings('ignore', category=FutureWarning, module=r'^torch\.nn\.utils\.weight_norm$')

# Jieba emits SyntaxWarnings for regex escape sequences and a pkg_resources deprecation UserWarning
warnings.filterwarnings('ignore', category=SyntaxWarning, module=r'^jieba(\.|$)')
warnings.filterwarnings('ignore', category=UserWarning, module=r'^jieba\._compat$')

from kokoro import KPipeline  # noqa: E402
import soundfile as sf  # noqa: E402
import sounddevice as sd  # noqa: E402

# Initialize pipeline globally (loaded once)
pipeline = None
current_lang_code = None

def get_lang_code_from_voice(voice):
    """Determine language code from voice prefix"""
    if voice.startswith('a'):
        return 'a'  # American English
    elif voice.startswith('b'):
        return 'b'  # British English
    elif voice.startswith('e'):
        return 'e'  # Spanish
    elif voice.startswith('f'):
        return 'f'  # French
    elif voice.startswith('h'):
        return 'h'  # Hindi
    elif voice.startswith('i'):
        return 'i'  # Italian
    elif voice.startswith('j'):
        return 'j'  # Japanese
    elif voice.startswith('p'):
        return 'p'  # Brazilian Portuguese
    elif voice.startswith('z'):
        return 'z'  # Mandarin Chinese
    return 'a'  # Default to American English

def ensure_unidic():
    """Download unidic dictionary if needed for Japanese"""
    try:
        import unidic
        from pathlib import Path
        import subprocess
        import sys
        if not Path(unidic.DICDIR).exists():
            print("Downloading Japanese dictionary (one-time setup)...")
            subprocess.run([sys.executable, '-m', 'unidic', 'download'], check=True)
    except ImportError:
        pass

def get_pipeline(lang_code='a'):
    global pipeline, current_lang_code
    if pipeline is None or current_lang_code != lang_code:
        # Ensure Japanese dictionary is available
        if lang_code == 'j':
            ensure_unidic()
        pipeline = KPipeline(lang_code=lang_code, repo_id='hexgrad/Kokoro-82M')
        current_lang_code = lang_code
    return pipeline

def text_to_speech(text, output_path, voice='af_heart', lang_code=None):
    """Convert text to speech and save as audio file"""
    if lang_code is None:
        lang_code = get_lang_code_from_voice(voice)
    pipeline = get_pipeline(lang_code)

    # Collect all audio chunks
    audio_chunks = []
    for gs, ps, audio in pipeline(text, voice=voice):
        audio_chunks.append(audio)

    # Concatenate all chunks
    full_audio = np.concatenate(audio_chunks)

    # Detect format from extension, default to MP3
    path_str = str(output_path)
    if path_str.endswith('.ogg'):
        sf.write(path_str, full_audio, 24000, format='OGG')
    elif path_str.endswith('.flac'):
        sf.write(path_str, full_audio, 24000, format='FLAC')
    elif path_str.endswith('.wav'):
        sf.write(path_str, full_audio, 24000, format='WAV')
    else:
        # Default to MP3
        sf.write(path_str, full_audio, 24000, format='MP3')

    return output_path

def speak(text, voice='af_heart', lang_code=None):
    """Play generated speech through the system audio output."""
    if lang_code is None:
        lang_code = get_lang_code_from_voice(voice)
    pipeline = get_pipeline(lang_code)

    # Stream chunks to output while collecting to avoid gaps
    audio_chunks = []
    for _, _, audio in pipeline(text, voice=voice):
        audio_chunks.append(audio)

    full_audio = np.concatenate(audio_chunks)
    sd.play(full_audio, samplerate=24000)
    sd.wait()

def main():
    parser = argparse.ArgumentParser(
        description='Convert text to speech using Kokoro TTS',
        epilog='''
Available voices:
  American English: af_heart, af_alloy, af_bella, af_nova, af_sarah, am_adam, am_michael, etc.
  British English: bf_alice, bf_emma, bf_isabella, bm_daniel, bm_george, etc.
  Japanese: jf_alpha, jm_kumo
  Chinese: zf_xiaobei, zm_yunxi
  Spanish: ef_dora, em_alex
  French: ff_siwis
  Hindi: hf_alpha, hm_omega
  Italian: if_sara, im_nicola
  Portuguese: pf_dora, pm_alex

Language codes (for -l flag):
  a=American English, b=British English, e=Spanish, f=French, h=Hindi,
  i=Italian, j=Japanese, p=Portuguese, z=Chinese
  Note: Language is auto-detected from voice prefix if -l is not specified

Full list: https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('text', nargs='?', help='Text to convert to speech (reads from stdin if omitted and piped)')
    parser.add_argument('-o', '--output', help='Output audio file path (default: output.mp3). Ignored when using --say',
                       default='output.mp3')
    parser.add_argument('-v', '--voice', help='Voice to use (default: af_heart)',
                       default='af_heart')
    parser.add_argument('-l', '--lang', help='Language code: a/b/e/f/h/i/j/p/z (auto-detected from voice if not specified)',
                       default=None)
    parser.add_argument('-s', '--say', action='store_true', help='Play audio through speakers instead of writing a file (ignores -o/--output)')

    args = parser.parse_args()

    # Resolve text from arg or stdin when piped
    input_text = args.text
    if input_text is None and not sys.stdin.isatty():
        input_text = sys.stdin.read().rstrip('\n')
    if not input_text:
        parser.error('No text provided. Pass TEXT or pipe input to stdin.')

    if args.say:
        print("Speaking...")
        try:
            speak(input_text, args.voice, args.lang)
        except Exception as e:
            print(f"Audio playback failed: {e}")
            return
        print("✓ Done")
        return
    output_path = Path(args.output)
    print("Generating speech...")
    result = text_to_speech(input_text, output_path, args.voice, args.lang)
    print(f"✓ Saved to {result}")

if __name__ == "__main__":
    main()
