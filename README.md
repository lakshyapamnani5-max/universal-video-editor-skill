# Universal Video Editor (UVE)

A general-purpose, local-first video editing skill for AI coding agents. It helps an agent plan edits, inspect footage, create an editable timeline, render with FFmpeg, and quality-check the result.

**Designed for:** Coders and creators using Codex, Claude Code, Gemini CLI, or OpenCode (subject to each host's skill support and local execution permissions).

## What it can do

- Cut, trim, reorder and join footage from an edit decision list.
- Export landscape, square and vertical video.
- Create contact sheets and inspect media metadata.
- Add titles, lower thirds and SRT captions.
- Mix background music and normalize audio.
- Apply basic colour adjustments and fades.
- Use modular editing styles and combine compatible styles.
- Includes an advanced production specification for presenter-led motion graphics, kinetic typography, animated infographics, UI cards and sound design.
- Includes an Editorial Motion Graphics style pack plus example scene and audio-FX plans.
- Optionally transcribe with faster-whisper.
- Preserve an editable JSON timeline and source media.

This is an agent skill plus a local editing toolkit, not a standalone GUI editor. The AI agent interprets requests and writes the timeline; FFmpeg performs deterministic media processing.

## Quick start

### Requirements

- Python 3.9+
- FFmpeg and ffprobe on PATH
- Optional: faster-whisper for local transcription
- Optional: ImageMagick is not required

### Install

Unzip this folder into the skill directory used by your agent:

| Agent | Typical skill directory |
|---|---|
| Codex | `~/.codex/skills/universal-video-editor/` |
| Claude Code | `~/.claude/skills/universal-video-editor/` |
| Gemini CLI | `~/.gemini/skills/universal-video-editor/` |
| OpenCode | `~/.config/opencode/skills/universal-video-editor/` |

Check the current documentation for your agent; paths and discovery behaviour may change.

Then run:

```bash
python scripts/uve.py setup
python scripts/uve.py doctor
```

Windows users can use `py` instead of `python` if needed.

## First project

```bash
python scripts/uve.py init "My First Edit" --out "./my-first-edit"
python scripts/uve.py probe "./media/clip.mp4"
python scripts/uve.py contact-sheet "./media/clip.mp4" --out "./my-first-edit/contact.jpg"
```

Edit `my-first-edit/edit.json` or ask your coding agent to create the edit plan from your brief and source footage. Then:

```bash
python scripts/uve.py render "./my-first-edit/edit.json" --out "./my-first-edit/exports/final.mp4"
python scripts/uve.py validate "./my-first-edit/exports/final.mp4"
```

## Styles

See `styles/index.json`. Each style contains a style guide and JSON preset. Styles can be combined by using one as the base and another as an accent. Avoid combining contradictory typography or colour systems.

## Advanced production (UVE 2.0 specification)

See `docs/UVE_2_UPGRADE.md` for the advanced pipeline and `styles/editorial-motion/STYLE.md` for the Editorial Motion Graphics style. Example scene and audio specifications are provided in `templates/motion-scene.example.json` and `templates/audio-fx.example.json`. These describe the target workflow for an AI agent or future renderer module; they are not all executable fields in the current basic FFmpeg renderer. The current renderer remains the reliable baseline for cuts, simple titles, fades, subtitles, music mixing and basic colour adjustments.

## Edit plan

See `templates/edit.example.json` for all supported fields. The agent should inspect source files and write accurate in/out points. The renderer validates paths and time ranges before rendering.

## Optional transcription

```bash
python scripts/uve.py transcribe "./media/interview.mp4" --out "./transcript.json" --model small
```

This installs no model automatically. Install `faster-whisper` separately if you want local transcription:

```bash
python -m pip install faster-whisper
```

## Platform notes

- FFmpeg filter availability varies by build. UVE uses common filters (`scale`, `crop`, `fps`, `concat`, `drawtext`, `subtitles`, `aresample`, `loudnorm`).
- Burning subtitles requires FFmpeg's subtitles/libass support.
- Font paths can differ between operating systems. Use a font file path in the edit plan for predictable title rendering.
- Hardware encoders are optional; the default renderer uses broadly supported `libx264`.
- Large projects need free disk space for intermediate files.

## Privacy

By default, processing is local. Optional transcription and AI-agent features depend on the software and model the user chooses. Do not upload user media without explicit permission.

## License

MIT. See `LICENSE`.
