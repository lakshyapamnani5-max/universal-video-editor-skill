# Edit plan reference

`edit.json` is the editable source of truth.

## Output
- `width`, `height`: output pixels.
- `fps`: frames per second.
- `crf`: H.264 quality (lower is higher quality).
- `preset`: FFmpeg x264 preset.

## Clips
- `src`: path relative to edit.json or absolute.
- `start`, `end`: source seconds.
- `fit`: `cover` or `contain`.
- `speed`: playback multiplier (1 = normal, 2 = twice as fast).
- `fade_in`, `fade_out`: seconds.
- `audio_gain`: source audio multiplier.

## Titles
- `text`, `start`, `duration`, `font_size`, `color`, `position` (`top`, `center`, `bottom`), optional `fontfile`, optional `box`.

## Captions
- `captions`: SRT path relative to edit.json or absolute. Requires FFmpeg subtitles filter.

## Audio
- `music`: optional audio file.
- `music_gain`: music volume multiplier.
- `normalize`: apply EBU-style loudness normalization near -14 LUFS.
