# Flingstone Audio Pack

Procedurally generated game audio concepts for Boris's `Flingstone` cue list.
The current pack renders three variants for every cue: the original email prompt `A` and `B` directions plus a new higher-fidelity `C` direction for all 14 sounds.

## Demo

A GitHub Pages soundboard demo is included in `index.html` so the pack can be previewed directly in the browser.

## Included Cues

1. `01_rubber_stretch_[a|b|c].wav`
2. `02_projectile_release_[a|b|c].wav`
3. `03_blocks_falling_[a|b|c].wav`
4. `04_core_hit_[a|b|c].wav`
5. `05_small_explosion_[a|b|c].wav`
6. `06_big_explosion_[a|b|c].wav`
7. `07_background_music_loop_[a|b|c].wav`
8. `08_ui_button_click_[a|b|c].wav`
9. `09_slow_motion_zoom_[a|b|c].wav`
10. `10_points_increase_[a|b|c].wav`
11. `11_victory_sound_[a|b|c].wav`
12. `12_unsuccessful_sound_[a|b|c].wav`
13. `13_clock_running_out_[a|b|c].wav`
14. `14_bonus_powerup_[a|b|c].wav`

## Notes

- These are higher-detail prototype assets meant to be immediately usable for creative review and iteration.
- All files are generated from `generate_sounds.py` so the pack is reproducible.
- Output format is mono `.wav` at 44.1 kHz for easy editing in common audio tools.
- The static demo uses the same rendered WAV files and supports per-cue A/B/C auditioning plus play-all across the selected cue variants.

## Regenerate

```bash
python3 generate_sounds.py
```
