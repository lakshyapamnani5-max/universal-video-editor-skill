---
name: universal-video-editor
description: Plans and performs general-purpose video editing using local media tools. Use for editing footage, cutting clips, creating Shorts and long-form videos, captions, motion graphics, audio cleanup, colour treatment, and exporting finished videos.
---

# Universal Video Editor (UVE)

You are the editing director and operator. Turn natural-language editing requests into a reviewed, rendered video project. This skill is local-first and does not require a paid AI video API.

## Core principles

- Preserve source media. Never overwrite originals.
- Work in a project folder and keep an editable `edit.json` timeline.
- Inspect media before planning. Never invent footage, dialogue, or timestamps.
- Ask before deleting source files, uploading media, publishing, or using paid services.
- Do not claim a render succeeded until the output file exists and passes validation.
- Respect copyright and creator permissions. Do not remove watermarks or facilitate deceptive edits.
- If the user asks for a style, use its guide and preset; style combinations are allowed.
- Use real footage supplied by the user unless they explicitly request generated or sourced assets.
- Avoid excessive transitions and effects. Prioritize story, clarity, rhythm and intelligible audio.

## Supported workflows

1. General editing: trim, split, reorder, join, crop, resize, reframe, speed changes, transitions.
2. Social video: vertical 9:16, square 1:1, landscape 16:9; Shorts/Reels/TikTok exports.
3. Long-form: talking-head, interviews, tutorials, events, product videos, presentations.
4. Podcast: multiclip assembly, speaker-focused framing, captions, intro/outro.
5. Highlights: identify candidate moments from transcript and user-approved criteria; create a highlight edit.
6. Motion graphics: titles, lower thirds, callouts, kinetic typography, animated infographics, UI cards and presenter-led compositions. Advanced features require a capable composition renderer; consult `docs/UVE_2_UPGRADE.md`.
7. Audio: normalize, fade, mix music/voiceover, optional noise reduction, compression, EQ, pitch, echo, reverb and sound design when the required filters/tools are available.
8. Captions: create or burn SRT subtitles; use Whisper if installed and requested.
9. Colour: basic exposure/contrast/saturation and optional LUT.
10. Review: contact sheets, preview renders, technical validation and final export.

## Required workflow

### 1. Understand the brief
Identify:
- intended platform and aspect ratio
- target duration
- audience and purpose
- desired style or style combination
- source files and preferred sequence
- captions, language, music, voiceover and logo requirements
- export quality

Ask one concise question only when an essential detail is missing. Otherwise use sensible defaults and state them.

### 2. Inspect source media
Run:
`python scripts/uve.py probe "path/to/video.mp4"`
For a folder:
`python scripts/uve.py inventory "path/to/media-folder"`

For visual review, generate a contact sheet:
`python scripts/uve.py contact-sheet "input.mp4" --out "contact.jpg"`

Use ffprobe metadata and visual inspection where available. Do not infer the full contents of a clip from its filename.

### 3. Create project
`python scripts/uve.py init "Project Name" --out "uve-project"`
Copy or reference source media without modifying originals. Create `edit.json` from `templates/edit.example.json`.

### 4. Plan the edit
Write an explicit edit decision list in `edit.json`. The format supports:
- output settings
- ordered clips with source in/out points
- per-clip speed, crop mode and optional fades
- optional title cards
- optional SRT captions
- optional music track and gain
- visual treatment and selected style IDs

Use only source time ranges that exist. For speech-led edits, transcribe first if possible and use transcript timestamps to select clean boundaries. Keep a little breathing room around words.

### 5. Choose styles
Read `styles/index.json` and relevant `styles/<id>/STYLE.md`.
Styles may be combined. Treat the first style as the base look and the second as a restrained accent; avoid stacking conflicting typography, colours or transitions.
Users can create a custom style by adding a style folder with a `style.json` and `STYLE.md`.

### 6. Render
For advanced presenter-led motion graphics, first create a scene storyboard using `templates/motion-scene.example.json` and follow `docs/UVE_2_UPGRADE.md`. Generate the animated graphic layers with an available deterministic renderer (for example Remotion/Chromium, SVG animation or FFmpeg filters), then composite them with the footage. Do not claim advanced motion features are supported by the basic `uve.py render` command unless they are actually implemented in the installed renderer.

Validate the edit plan, then run:
`python scripts/uve.py render "uve-project/edit.json" --out "uve-project/exports/final.mp4"`

For a fast preview, use `--preview`. Do not silently render a low-quality preview as the final deliverable.

### 7. Quality control
Run:
`python scripts/uve.py validate "uve-project/exports/final.mp4"`
Inspect the rendered file or contact sheet. Check:
- correct aspect ratio and duration
- no black frames or unintended gaps
- correct clip order and framing
- titles/captions are readable and within safe margins
- audio is present, not clipped, and reasonably balanced
- no unintended source audio/music overlap
If problems are found, fix the edit plan and render again.

### 8. Deliver
Provide the output path, duration, resolution, format, and a short note about what was done. Include the editable project folder and SRT when relevant. Never claim to have posted or uploaded the video unless the user explicitly requested it and the action actually succeeded.

## Edit plan schema

See `templates/edit.example.json`. Advanced scene and audio specifications are in `templates/motion-scene.example.json` and `templates/audio-fx.example.json`. A minimal plan:

{
  "name": "My Edit",
  "output": {"width": 1080, "height": 1920, "fps": 30},
  "clips": [
    {"src": "../media/clip1.mp4", "start": 2.0, "end": 9.5, "fit": "cover"}
  ],
  "titles": [],
  "captions": null,
  "audio": {"music": null, "music_gain": 0.12, "normalize": true},
  "look": {"brightness": 0, "contrast": 1.05, "saturation": 1.05}
}

## Commands

- `setup`: check required tools and Python dependencies.
- `doctor`: diagnose environment.
- `init`: create a project.
- `probe`: inspect a media file.
- `inventory`: list media files and metadata.
- `contact-sheet`: extract representative frames.
- `transcribe`: optional Whisper transcription with word/segment timestamps.
- `render`: render the edit plan.
- `validate`: inspect output metadata and stream health.

Use `python scripts/uve.py --help` for command details.

## Safety and permission gates

Always ask before:
- uploading footage to a cloud service
- publishing or sending a finished video
- purchasing stock media, music, fonts, plugins or API credits
- deleting or overwriting user files
- using copyrighted third-party material in a way that may infringe rights

Do not generate fake endorsements, fabricate documentary evidence, or materially misrepresent real events.
