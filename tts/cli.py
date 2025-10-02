import os
import platform
import warnings
import argparse
from pathlib import Path
import numpy as np

# Enable MPS fallback on macOS
if platform.system() == 'Darwin':
    os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'

# Suppress PyTorch warnings
warnings.filterwarnings('ignore', category=UserWarning, module='torch.nn.modules.rnn')
warnings.filterwarnings('ignore', category=FutureWarning, module='torch.nn.utils.weight_norm')

from kokoro import KPipeline  # noqa: E402
import soundfile as sf  # noqa: E402

# Initialize pipeline globally (loaded once)
pipeline = None

def get_pipeline():
    global pipeline
    if pipeline is None:
        pipeline = KPipeline(lang_code='a', repo_id='hexgrad/Kokoro-82M')
    return pipeline

def text_to_speech(text, output_path, voice='af_heart'):
    """Convert text to speech and save as audio file"""
    pipeline = get_pipeline()

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

Full list: https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('text', help='Text to convert to speech')
    parser.add_argument('-o', '--output', help='Output audio file path (default: output.mp3)',
                       default='output.mp3')
    parser.add_argument('-v', '--voice', help='Voice to use (default: af_heart)',
                       default='af_heart')

    args = parser.parse_args()

    output_path = Path(args.output)

    print("Generating speech...")
    result = text_to_speech(args.text, output_path, args.voice)
    print(f"✓ Saved to {result}")

if __name__ == "__main__":
    main()
