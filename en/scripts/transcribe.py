"""Speech transcription from video or audio (faster-whisper, large-v3-turbo model).

Examples:
  python transcribe.py video.mp4 --out work/transcript.txt                  # text with timestamps (to watch a video)
  python transcribe.py video.mp4 --out work/transcript.json --format words  # for embedded-captions
  python transcribe.py video.mp4 --out work/transcript.json --format flat   # for talking-head-recut

An NVIDIA GPU is used automatically if present; otherwise transcription runs on the CPU (slower).
Audio is extracted with ffmpeg (taken from PATH or from the FFMPEG environment variable).
"""
import argparse
import json
import os
import shutil
import site
import subprocess
import sys
import tempfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")  # readable output in the Windows console
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

# Windows: NVIDIA libraries (pip install nvidia-cublas-cu12 nvidia-cudnn-cu12) live inside Python —
# tell Windows where their DLLs are. Nothing needed on Mac or Linux.
if sys.platform == "win32":
    for base in [*site.getsitepackages(), site.getusersitepackages()]:
        for sub in ("cublas", "cudnn", "cuda_nvrtc"):
            p = Path(base) / "nvidia" / sub / "bin"
            if p.is_dir():
                os.add_dll_directory(str(p))
                os.environ["PATH"] = str(p) + os.pathsep + os.environ["PATH"]

from faster_whisper import WhisperModel  # noqa: E402

FFMPEG = os.environ.get("FFMPEG") or shutil.which("ffmpeg")


def to_wav(src: Path, dst: Path) -> None:
    if not FFMPEG:
        sys.exit("ffmpeg not found: install it or set its path in the FFMPEG environment variable.")
    subprocess.run([FFMPEG, "-v", "error", "-y", "-i", str(src), "-vn", "-ac", "1", "-ar", "16000", str(dst)], check=True)


def load_model(name: str, cpu: bool, compute: str | None):
    if not cpu:
        try:
            return WhisperModel(name, device="cuda", compute_type=compute or "float16"), "cuda"
        except Exception as e:  # no NVIDIA GPU or CUDA libraries missing
            print(f"GPU not available ({str(e).splitlines()[0][:120]}), using the CPU — this is slower")
    return WhisperModel(name, device="cpu", compute_type="int8"), "cpu"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("media")
    ap.add_argument("--out", required=True)
    ap.add_argument("--format", choices=["text", "words", "flat"], default="text")
    ap.add_argument("--language", default=None, help="en, ru… (detected automatically by default)")
    ap.add_argument("--model", default="large-v3-turbo", help="model name or path to your own faster-whisper model folder (see settings.md)")
    ap.add_argument("--cpu", action="store_true", help="do not try the GPU")
    ap.add_argument("--compute", default=None, help="GPU precision: float16 (default) or int8_float16 for 4 GB cards")
    a = ap.parse_args()

    src = Path(a.media)
    with tempfile.TemporaryDirectory(prefix="video_ru_") as tmp:
        wav = Path(tmp) / "audio.wav"
        to_wav(src, wav)
        model, device = load_model(a.model, a.cpu, a.compute)
        segments, info = model.transcribe(
            str(wav), language=a.language, beam_size=5, vad_filter=True,
            word_timestamps=a.format != "text",
        )
        segments = list(segments)

    duration = info.duration
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    if a.format == "text":
        lines = []
        for s in segments:
            m, sec = divmod(int(s.start), 60)
            lines.append(f"[{m:02d}:{sec:02d}] {s.text.strip()}")
        out.write_text("\n".join(lines), encoding="utf-8")
    else:
        words = []
        for s in segments:
            for w in s.words or []:
                text = w.word.strip()
                if not text:
                    continue
                start = round(max(0.0, w.start), 3)
                end = round(min(duration, max(w.end, start + 0.05)), 3)  # not past the end of the file
                words.append({"text": text, "start": start, "end": end})
        # word times must only increase
        for prev, cur in zip(words, words[1:]):
            if cur["start"] < prev["end"]:
                prev["end"] = cur["start"]
        if a.format == "words":
            data = {"words": [dict(w, type="word") for w in words]}
        else:
            data = words
        out.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"language: {info.language} ({info.language_probability:.0%}), length: {duration:.1f} s, device: {device}")
    print(f"done: {out}")


if __name__ == "__main__":
    main()
