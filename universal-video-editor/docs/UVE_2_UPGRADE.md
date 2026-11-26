# UVE 2.0 — Advanced Production Engine Specification

This document defines the advanced production workflow UVE agents should follow. It is an implementation specification, not a claim that every feature is already implemented by the v1.0 FFmpeg renderer.

## Target output style: Editorial Motion Graphics

Designed for presenter-led explainers and promotional videos like the user-provided reference:
- 9:16, 1080x1920 or 4K vertical master
- warm off-white / cream backgrounds
- deep charcoal typography with one brand accent colour
- talking-head footage in a stable lower or side panel
- animated headlines, strike-throughs, underlines and emphasis words
- floating UI cards, charts, diagrams and number counters
- clean scene changes, not random transition spam
- restrained whooshes, clicks, impacts and music ducking

## Production pipeline

1. **Ingest** — probe all media, create contact sheets, identify aspect ratios, audio streams and durations.
2. **Understand** — transcribe speech with word timestamps where available. Extract claims, key phrases, entities, numbers and scene boundaries. Do not invent facts or chart values.
3. **Storyboard** — create a scene list with narration ranges, purpose, layout, visual assets, motion, audio cues and duration.
4. **Design system** — define canvas, safe areas, fonts, palette, spacing, corner radii, shadows and reusable components.
5. **Compose** — generate motion graphic overlays as SVG/HTML/CSS or native FFmpeg layers. Use a deterministic renderer such as Remotion/Chromium when available; fall back to SVG/FFmpeg when not.
6. **Edit presenter** — crop/reframe the presenter, preserve eye-line and headroom, use picture-in-picture only when the storyboard calls for it.
7. **Sound design** — process voice separately, add music and spot effects, duck music under speech, and loudness-normalize the master.
8. **Render** — render scene assets, composite with footage, encode a high-quality master and social variants.
9. **QC** — inspect contact sheets and listen to the complete export. Check text, timing, safe margins, audio peaks, clipping, black frames and sync.
10. **Deliver** — MP4, editable edit plan, storyboard, captions, asset manifest and any generated overlay source files.

## Scene planning rules

Each scene must have:
- `id`, `start`, `end`, `narration` or transcript range
- `layout`: `presenter_full`, `presenter_bottom`, `presenter_side`, `full_graphic`, `picture_in_picture`
- `background`: colour, image or video
- `elements`: title, emphasis text, chart, stat card, icon, UI card, line/shape or image
- `animation`: enter, hold and exit behaviour with durations
- `audio_cues`: optional sound effect IDs and timing

Keep important text inside 8% horizontal and 10% vertical safe margins for 9:16. Avoid covering the presenter's face. Use no more than two typefaces and three core colours per video unless the brand guide specifies otherwise.

## Motion vocabulary

Supported target presets:
- `fade`: opacity ramp
- `slide_up`, `slide_down`, `slide_left`, `slide_right`
- `scale_in`, `pop`, `spring` (subtle overshoot)
- `wipe`: masked reveal
- `type_on`: character reveal for short labels only
- `draw_on`: line/chart path reveal
- `counter`: numeric count-up with source-grounded values
- `stagger`: sequential entrance for grouped elements
- `parallax`: small depth offset between layers
- `blur_in`: blur-to-sharp reveal

Motion should communicate hierarchy. Do not animate every element simultaneously. Respect reduced-motion requests.

## Graphics generation

- Use SVG for crisp vector graphics, charts, icons and UI cards.
- Use HTML/CSS/Remotion or a browser renderer for complex timed compositions when installed.
- Use Three.js only when actual 3D adds value; render 3D scenes to image/video assets before final FFmpeg composition.
- Use source-grounded numbers only. If data is missing, use abstract decorative graphics rather than fabricated charts.
- Use licensed or user-provided fonts, music and assets.

## Presenter layout rules

- Detect or manually establish the presenter crop from source footage.
- Keep the presenter visible during key spoken moments.
- When switching the speaker panel from top to bottom, animate only if it improves comprehension.
- Do not crop eyes, chin or hands during gestures.
- Use background removal only when a reliable segmentation model is installed; otherwise use a clean rounded video panel.

## Audio FX chain

Recommended voice chain (adjust conservatively):
1. high-pass rumble removal around 70–100 Hz where appropriate
2. optional noise reduction (arnndn/afftdn when available)
3. gentle compression
4. subtle EQ / presence lift
5. de-esser only when needed and available
6. limiter / loudness normalization

Optional creative FX: room reverb, slap delay, telephone/radio band-pass, pitch shift, distortion, stereo widening and reverse/impact transitions. Keep dialogue intelligible. Never apply a dramatic voice effect without user intent or a clearly appropriate creative brief.

Music and SFX:
- duck music while speech is active
- keep whooshes and impacts below dialogue
- align effects to visual events
- avoid clipping and sudden loudness jumps
- ensure the user has rights to supplied/licensed audio

## Capability honesty

The existing UVE v1.0 renderer supports deterministic cuts, basic fades, simple text overlays, SRT subtitles, music mixing, loudness normalization and basic colour adjustments. Advanced animated typography, chart animation, layered motion graphics, voice FX and intelligent scene-to-speech synchronization require additional renderer modules and dependencies. Never claim these have rendered unless the actual export contains them and has passed QC.
