"""Расшифровка речи из видео или аудио (faster-whisper, модель large-v3-turbo).

Примеры:
  python transcribe.py video.mp4 --out work/transcript.txt                  # текст с таймкодами (посмотреть видео)
  python transcribe.py video.mp4 --out work/transcript.json --format words  # для embedded-captions
  python transcribe.py video.mp4 --out work/transcript.json --format flat   # для talking-head-recut

Видеокарта NVIDIA используется сама, если она есть; иначе расшифровка идёт на процессоре (медленнее).
Звук из видео вытаскивается через ffmpeg (берётся из PATH или из переменной FFMPEG).
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

sys.stdout.reconfigure(encoding="utf-8")  # русские сообщения в консоли Windows без кракозябр
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

# Windows: библиотеки NVIDIA (pip install nvidia-cublas-cu12 nvidia-cudnn-cu12) лежат внутри Python —
# подсказываем, где их DLL. На Mac и Linux ничего не нужно.
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
        sys.exit("Не найден ffmpeg: поставьте его или укажите путь в переменной FFMPEG.")
    subprocess.run([FFMPEG, "-v", "error", "-y", "-i", str(src), "-vn", "-ac", "1", "-ar", "16000", str(dst)], check=True)


def load_model(name: str, cpu: bool, compute: str | None):
    if not cpu:
        try:
            return WhisperModel(name, device="cuda", compute_type=compute or "float16"), "cuda"
        except Exception as e:  # нет видеокарты NVIDIA или не хватает библиотек CUDA
            print(f"видеокарта недоступна ({str(e).splitlines()[0][:120]}), считаю на процессоре — это медленнее")
    return WhisperModel(name, device="cpu", compute_type="int8"), "cpu"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("media")
    ap.add_argument("--out", required=True)
    ap.add_argument("--format", choices=["text", "words", "flat"], default="text")
    ap.add_argument("--language", default=None, help="ru, en… (по умолчанию определяется сам)")
    ap.add_argument("--model", default="large-v3-turbo", help="имя модели или путь к папке своей модели faster-whisper (см. настройки.md)")
    ap.add_argument("--cpu", action="store_true", help="не пробовать видеокарту")
    ap.add_argument("--compute", default=None, help="точность на видеокарте: float16 (по умолчанию) или int8_float16 для 4 ГБ")
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
                end = round(min(duration, max(w.end, start + 0.05)), 3)  # не дальше конца файла
                words.append({"text": text, "start": start, "end": end})
        # время слов должно только расти
        for prev, cur in zip(words, words[1:]):
            if cur["start"] < prev["end"]:
                prev["end"] = cur["start"]
        if a.format == "words":
            data = {"words": [dict(w, type="word") for w in words]}
        else:
            data = words
        out.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"язык: {info.language} ({info.language_probability:.0%}), длина: {duration:.1f} c, устройство: {device}")
    print(f"готово: {out}")


if __name__ == "__main__":
    main()
