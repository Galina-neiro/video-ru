# video-ru / video-en

**Русский** · [English](#english)

Скилл для Claude Code, с которого начинается любая работа с видео на русском:
- посмотреть и разобрать ролик по файлу или ссылке (YouTube, VK, Rutube, Instagram): расшифровка с таймкодами
  и кадры «листами»;
- точная русская расшифровка по словам (на видеокарте NVIDIA, если она есть) — по ней субтитры и плашки
  встают ровно под речь;
- подсказывает, какой скилл HyperFrames (HeyGen) брать для субтитров, плашек, анимации, наездов камеры;
- правила для русских субтитров: шрифты с кириллицей, предлоги не висят в конце строки, «ёлочки», безопасные зоны Reels.

Автор — Галина Салий, TG-канал [@galina_saliy_pro](https://t.me/galina_saliy_pro).
Внутри текстовые файлы и один короткий скрипт на Python ([scripts/transcribe.py](scripts/transcribe.py)):
их можно открыть и прочитать перед установкой.

## Что нужно

Работает только в Claude Code (приложение, VS Code или терминал), на сайте claude.ai — нет: нужны программы
на компьютере. Скилл сам проверит и, с вашего согласия, поставит недостающее: ffmpeg, Python с faster-whisper
и yt-dlp, Node.js, скиллы HyperFrames (github.com/heygen-com/hyperframes). Видеокарта не обязательна,
без неё расшифровка медленнее. При первом запуске Клод посмотрит вашу видеокарту и уже стоящий Whisper
(второй ставить не будет), подберёт модель и запишет всё в настройки.md — дальше без проверок.
Модель Whisper (~1,6 ГБ), если её нет, скачается при первой расшифровке.

## Как поставить

Отправьте Claude Code:

> Поставь скилл из https://github.com/Galina-neiro/video-ru (корень репозитория, без папки en) в папку ~/.claude/skills/video-ru (чтобы он работал во всех папках), потом пройди раздел «Первый запуск» из его SKILL.md и скажи, чего у меня не хватает.

Или скачайте архив **[video-ru.zip](https://github.com/Galina-neiro/video-ru/releases/latest/download/video-ru.zip)**, положите в любую папку, откройте её в Claude Code и напишите:

> Распакуй архив video-ru.zip в папку ~/.claude/skills (чтобы скилл работал во всех папках), потом пройди раздел «Первый запуск» из его SKILL.md и скажи, чего у меня не хватает.

После установки перезапустите Claude Code, чтобы он увидел новый скилл.

## Как пользоваться

Напишите Клоду: «посмотри видео <путь к файлу или ссылка>», «расшифруй», «сделай субтитры к рилсу»,
«добавь плашки», «сделай заставку». Чтобы ролики были в вашем стиле — заполните бренд.md
(шрифты, цвета, акценты) или скажите Клоду, и он заполнит его вместе с вами.

---

## English

A Claude Code skill to start any video task with:
- watch and break down a video from a file or a link (YouTube, TikTok, Instagram, Vimeo): transcript with
  timestamps and contact sheets of frames;
- accurate word-level transcription (on an NVIDIA GPU if you have one) so captions and cards land exactly on the words;
- tells Claude which HyperFrames (HeyGen) skill to use for captions, overlays, animation, camera moves;
- caption rules for short-form video: line breaks, accents, Reels/TikTok safe zones.

Made by Galina Saliy, a graphic and web designer from Russia (Telegram: [@galina_saliy_pro](https://t.me/galina_saliy_pro), in Russian).
Plain text files and one short Python script ([en/scripts/transcribe.py](en/scripts/transcribe.py)) —
you can open and read them before installing. The English skill lives in the [en](en) folder.

### What you need

Works only in Claude Code (desktop app, VS Code or terminal), not on claude.ai: it needs programs on your
computer. The skill checks and, with your consent, installs what's missing: ffmpeg, Python with faster-whisper
and yt-dlp, Node.js, the HyperFrames skills (github.com/heygen-com/hyperframes). A GPU is optional, without one
transcription is slower. On the first run Claude looks at your GPU and any Whisper you already have (it won't
install a second one), picks a model and records everything in settings.md — no checks after that.
The Whisper model (~1.6 GB), if you don't have it, downloads on the first transcription.

### How to install

Send this to Claude Code:

> Install the skill from https://github.com/Galina-neiro/video-ru (the en folder) into ~/.claude/skills/video-en (so it works in every folder), then go through the "First run" section of its SKILL.md and tell me what I'm missing.

Or download **[video-en.zip](https://github.com/Galina-neiro/video-ru/releases/latest/download/video-en.zip)**, put it in any folder, open that folder in Claude Code and send:

> Unzip video-en.zip into ~/.claude/skills (so the skill works in every folder), then go through the "First run" section of its SKILL.md and tell me what I'm missing.

Restart Claude Code after installing so it picks up the new skill.

### How to use

Tell Claude: "watch this video <file path or link>", "transcribe", "add captions to my reel",
"add overlays", "make an intro". To get videos in your style, fill in brand.md (fonts, colors, accents)
or ask Claude and it will fill it in with you.

---

## Лицензия / License

MIT, см. / see [LICENSE](LICENSE). Скиллы HyperFrames сюда не входят / HyperFrames skills are not included —
[heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) (Apache 2.0).
