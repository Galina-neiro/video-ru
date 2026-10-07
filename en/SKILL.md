---
name: video-en
description: |
  Video work: watch and break down a video or reel (from a file path or a YouTube/TikTok/Instagram/Vimeo link),
  transcribe speech, download a clip, and make captions, graphic overlays or short animations with HyperFrames.
  Use FIRST for any video or audio task: "watch this video", "what's in this reel", "transcribe", "add captions",
  "add overlays", "edit my reel", "make an intro". Tells which HyperFrames skill to use next and prepares an
  accurate word-level transcript (on the GPU if there is one).
metadata:
  version: "1.0.0"
---

# Video

This skill is a thin layer. The heavy lifting is done by programs (ffmpeg, Whisper) and the official HyperFrames skills by HeyGen; this file holds only the routing and the rules for captioned short-form video. Read only the HyperFrames skill the task needs, not all of them.

## First run: set up for this computer

Works only in Claude Code (desktop app, VS Code or terminal): it needs programs on the computer.

**First read `settings.md` next to this file.** If the computer is already recorded there, skip the checks and use the commands from it (which python, ffmpeg path, model, `--cpu` or not). If the file is empty or something recorded stopped working, run the setup below and write the result there.

Setup — once:

| What | Check | Why |
|---|---|---|
| ffmpeg / ffprobe | `ffmpeg -version` | audio and frames from video |
| Python 3.10+ with faster-whisper and yt-dlp | `python -c "import faster_whisper, yt_dlp"` (on Mac — `python3`) | transcription, downloading from links |
| Node.js | `node -v` | HyperFrames |
| HyperFrames skills | is the `hyperframes` skill in the skills list | editing, overlays, animation |
| NVIDIA GPU (optional) | `nvidia-smi` (name and memory) | transcription dozens of times faster |
| An existing Whisper | `pip list` (faster-whisper, openai-whisper, whisperx), model folders, ask the user | don't install a second one |

**Their own Whisper.** If the user already has faster-whisper and downloaded models, don't install another: pass the model folder to the script with `--model <path>` or point `HF_HOME` at their cache. If they have a different Whisper (openai-whisper, whisper.cpp, whisperx), ask whether to keep it. If yes, transcribe with it and convert the result to our script's format (`words`: `{"words":[{"text","start","end","type":"word"}]}`, `flat`: the same word list without the wrapper) — that is the format the HyperFrames skills expect.

**Model for the GPU** (faster-whisper):

| Computer | Use |
|---|---|
| NVIDIA with 6 GB+ | `large-v3-turbo` on the GPU (default) — best quality |
| NVIDIA 4 GB | `large-v3-turbo` with `--compute int8_float16`, or `--model medium` |
| No NVIDIA (incl. Mac, AMD, laptops with integrated graphics) | `--cpu`, model `small` (fast) or `large-v3-turbo` (more accurate, several times slower) |

Test on a short piece (`ffmpeg -t 10`) of the user's own video: if the GPU run fails with a CUDA or memory error, install the libraries below or take a smaller model. Show the user speed and quality and choose together. For English-only content `small.en` / `medium.en` are also an option on slow machines.

If something is missing, list for the user what it is and how big, and **install only with their consent**. On Windows ask which drive to use if C is short on space.
- ffmpeg, Node, Python: Windows — `winget install Gyan.FFmpeg`, `winget install OpenJS.NodeJS.LTS`, `winget install Python.Python.3.12`; Mac — `brew install ffmpeg node python`.
- Libraries: `python -m pip install faster-whisper yt-dlp`. Windows with an NVIDIA GPU — also `python -m pip install nvidia-cublas-cu12 "nvidia-cudnn-cu12==9.*"`.
- HyperFrames skills: `npx skills add heygen-com/hyperframes --all` (github.com/heygen-com/hyperframes, Apache 2.0).
- The Whisper model (~1.6 GB) downloads itself on the first transcription into the HuggingFace cache. Another location — the `HF_HOME` variable.
- If the user wants: turn off HyperFrames telemetry with `HYPERFRAMES_NO_TELEMETRY=1` and `DO_NOT_TRACK=1`.

**At the end of setup, write everything to `settings.md`** (following the template in the file): which python and ffmpeg, GPU, chosen model and flags, where the model cache is, speed on the test. From then on run the commands in sections A and B with those flags.

Our transcription script is `scripts/transcribe.py` next to this file. It uses the GPU on its own and falls back to the CPU without one. Flags: `--model` (name or path to your own model), `--compute`, `--cpu`, `--language`.

Don't send HyperFrames "feedback" reports after rendering without asking. Run `npx hyperframes skills update` only with the user's consent.

## A. Watch and break down a video

1. **Get the file.** Take a file path as is; never modify the original. Download a link into a temporary folder:
   `python -m yt_dlp --no-playlist -o "<folder>/video.%(ext)s" --print-to-file "%(uploader)s | %(duration)s s | %(like_count)s likes | %(comment_count)s comments | %(description)s" "<folder>/info.txt" <link>`
   For YouTube, if only the text is needed, try subtitles first: `--write-auto-subs --sub-langs en --skip-download`. Instagram and private channels may require login — then ask the user to download the file themselves.
2. **Inspect the file:** `ffprobe -v error -show_entries format=duration:stream=codec_type,width,height -of compact <video>`.
3. **Transcribe:** `python scripts/transcribe.py <video> --out <folder>/transcript.txt` (text with timestamps).
4. **Contact sheets** (12 frames per image — saves tokens):
   vertical: `ffmpeg -v error -y -i <video> -vf "fps=1/2,scale=216:-2,tile=6x2:padding=4:color=white" <folder>/sheet_%02d.jpg`
   horizontal: the same with `scale=320:-2,tile=4x3`. For videos over 2 minutes — `fps=1/5` or `1/10`. Read the sheets as images.
5. **Answer:** author and numbers (if any), the format of the video, the transcript (or a summary if long), what's on screen, and separately — what's useful for the user. If the video exaggerates, say so honestly.

## B. Make a video with HyperFrames

**Which skill to use:**

| Task | Skill |
|---|---|
| any video, the starting point; when unsure what to use | `hyperframes` (main entry, routes on its own) |
| captions for a talking-to-camera video: 1–3 words, key words in color, karaoke | `embedded-captions` |
| graphics over a talking-head video: cards, icons, "on a phone" inserts, split screen, picture-in-picture circle | `talking-head-recut` |
| a short animation without speech up to ~30 s: intro, numbers, logo, UI mockups, before → after | `motion-graphics` |
| structure of the video: layers, when each card appears, video inserts | `hyperframes-core` |
| how cards slide in, stickers, full-frame word "hits", kinetic type | `hyperframes-animation` |
| camera push-ins and pull-outs, smooth zooms | `hyperframes-keyframes` |
| music, sound effects, icons, processing inserts | `media-use` |
| checks, rendering to MP4, background removal ("from behind the shoulder" inserts) | `hyperframes-cli` |
| ready-made effects (glitch, confetti, charts), music volume under the voice, colors and fonts | `hyperframes-registry`, `hyperframes-audio`, `hyperframes-creative` |

By HyperFrames rules the `hyperframes` skill is read first; for simple tasks its SKILL.md is enough, without the references.

**Prepare the transcript with our script** (accurate word timing, uses the GPU), rather than the built-in `hyperframes transcribe`:
- for `embedded-captions`: `python scripts/transcribe.py <video> --out <work folder>/transcript.json --format words` — the skill picks up the ready `transcript.json`;
- for `talking-head-recut`: the same with `--format flat` (a flat word array), skip the skill's transcription step.
Before using it, read the transcript and fix recognition errors (names, brands, terms). Show the user the list of fixes in one line.

**Project:** ask which folder to use. Inside: `sources/` (copies of the source files — never modify or delete the originals), the HyperFrames working files, `done/` for the final MP4s.

**Formats:** Reels/Shorts/Stories/TikTok — 1080×1920, 9:16, 30 fps; YouTube — 1920×1080; feed post — 1080×1350.

## Captions and on-screen text

- The font must have every glyph the text needs (accents, other alphabets if the video is multilingual) — check before rendering. Prefer a local `.woff2` in the project folder over Google Fonts over the network.
- 2–4 words per line. Don't end a line on an article, preposition or conjunction (a, an, the, of, to, in, on, and, but) — move it to the next word.
- Numbers as digits, curly quotes and apostrophes, real em dashes.
- ALL CAPS only for short accents (1–3 words), not whole sentences.
- Captions must not cover the face or the bottom UI zone of Reels/TikTok (buttons, caption) — keep to the safe zone. Put the hook in the center of the frame or slightly lower, not at the top edge.
- If `brand.md` in the skill folder is filled in (fonts, colors, how to accent) — use it. If it's empty, ask the user about their style once and offer to save the answer there.

## Before saying "done"

Show the plan (what, where, which style) before a long render. After rendering, cut a contact sheet from the result (A4) and look yourself: text is readable, doesn't run off the edge, all glyphs render, in sync with speech. Only then give the user the path to the file in `done/`.
