# Flingstone Audio Pack

Procedurally generated placeholder game audio for Boris's `Flingstone` cue list.

## Included Cues

1. `01_rubber_stretch.wav`
2. `02_projectile_release.wav`
3. `03_blocks_falling.wav`
4. `04_core_hit.wav`
5. `05_small_explosion.wav`
6. `06_big_explosion.wav`
7. `07_background_music_loop.wav`
8. `08_ui_button_click.wav`
9. `09_slow_motion_zoom.wav`
10. `10_points_increase.wav`
11. `11_victory_sound.wav`
12. `12_unsuccessful_sound.wav`
13. `13_clock_running_out.wav`
14. `14_bonus_powerup.wav`

## Notes

- These are lightweight starter assets meant to be immediately usable for prototyping.
- All files are generated from `generate_sounds.py` so the pack is reproducible.
- Output format is mono `.wav` at 44.1 kHz for easy editing in common audio tools.

## Regenerate

```bash
python3 generate_sounds.py
```
