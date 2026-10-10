"""Prepare and check the local speech model, outside any session.

    python -m lecoach.speech.model --download   # fetch the configured weights into models/
    python -m lecoach.speech.model --check      # load them and time a silent transcription

Requires the optional `speech` dependency group. Downloading needs the network
once; sessions only ever load the prepared files.
"""

import argparse
import sys
import time
from array import array
from pathlib import Path

from .config import SpeechConfig
from .whisper import WHISPER_RATE, ModelUnavailable, load_transcriber, model_path


def download(config: SpeechConfig) -> Path:
    from faster_whisper.utils import download_model

    return Path(download_model(config.model, output_dir=str(model_path(config))))


def check(config: SpeechConfig) -> dict:
    started = time.perf_counter()
    transcriber = load_transcriber(config)
    loaded = time.perf_counter()
    result = transcriber.transcribe(array("f", bytes(4 * WHISPER_RATE)), WHISPER_RATE, final=True)
    return {"load_s": round(loaded - started, 2),
            "silent_transcription_s": round(time.perf_counter() - loaded, 2),
            "silent_text": result.text}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m lecoach.speech.model",
                                     description="Prepare the local speech model.")
    parser.add_argument("--download", action="store_true", help="download the model weights")
    parser.add_argument("--check", action="store_true", help="load the model and time it")
    parser.add_argument("--model", help="model name (default: SpeechConfig.model)")
    parser.add_argument("--model-dir", help="model directory (default: models)")
    args = parser.parse_args(argv)
    if not (args.download or args.check):
        parser.error("choose --download and/or --check")
    overrides = {"model": args.model, "model_dir": args.model_dir}
    config = SpeechConfig(**{key: value for key, value in overrides.items() if value})
    try:
        if args.download:
            print(f"downloading {config.model} ...", flush=True)
            print(f"ready: {download(config)}")
        if args.check:
            print(check(config))
    except ImportError as error:
        print(f"speech runtime missing ({error}); run: uv sync --frozen --group speech",
              file=sys.stderr)
        return 2
    except ModelUnavailable as error:
        print(error, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
