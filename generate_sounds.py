#!/usr/bin/env python3
from __future__ import annotations

import math
import os
import wave
from pathlib import Path

import numpy as np

SR = 44100
ASSET_DIR = Path(__file__).parent / "assets"


def env(length: int, attack: float = 0.01, decay: float = 0.1, sustain: float = 0.6, release: float = 0.1) -> np.ndarray:
    a = max(1, int(length * attack))
    d = max(1, int(length * decay))
    r = max(1, int(length * release))
    s = max(0, length - a - d - r)
    out = np.concatenate(
        [
            np.linspace(0, 1, a, endpoint=False),
            np.linspace(1, sustain, d, endpoint=False),
            np.full(s, sustain),
            np.linspace(sustain, 0, r, endpoint=True),
        ]
    )
    if len(out) < length:
        out = np.pad(out, (0, length - len(out)))
    return out[:length]


def tone(freq: float, dur: float, amp: float = 1.0, phase: float = 0.0) -> np.ndarray:
    t = np.arange(int(SR * dur)) / SR
    return amp * np.sin(2 * math.pi * freq * t + phase)


def chirp(f0: float, f1: float, dur: float, amp: float = 1.0) -> np.ndarray:
    t = np.arange(int(SR * dur)) / SR
    k = (f1 - f0) / max(dur, 1e-9)
    return amp * np.sin(2 * math.pi * (f0 * t + 0.5 * k * t * t))


def noise(dur: float, amp: float = 1.0, seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return amp * rng.standard_normal(int(SR * dur))


def lowpass(x: np.ndarray, win: int = 300) -> np.ndarray:
    if win <= 1:
        return x
    kernel = np.ones(win) / win
    return np.convolve(x, kernel, mode="same")


def bandish_noise(dur: float, amp: float, seed: int, low_win: int, hi_mix: float = 0.0) -> np.ndarray:
    n = noise(dur, 1.0, seed)
    lp = lowpass(n, low_win)
    return amp * ((1 - hi_mix) * lp + hi_mix * n)


def normalize(x: np.ndarray, peak: float = 0.92) -> np.ndarray:
    m = np.max(np.abs(x)) if len(x) else 0.0
    if m > 0:
        x = x * (peak / m)
    return x


def save(name: str, data: np.ndarray) -> None:
    data = normalize(data)
    pcm = np.int16(np.clip(data, -1.0, 1.0) * 32767)
    path = ASSET_DIR / name
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm.tobytes())


def layer(*parts: np.ndarray) -> np.ndarray:
    length = max(len(p) for p in parts)
    out = np.zeros(length)
    for part in parts:
        out[: len(part)] += part
    return out


def place(base: np.ndarray, clip: np.ndarray, at_sec: float) -> np.ndarray:
    i = int(at_sec * SR)
    if i + len(clip) > len(base):
        base = np.pad(base, (0, i + len(clip) - len(base)))
    base[i : i + len(clip)] += clip
    return base


def rubber_stretch() -> np.ndarray:
    dur = 1.2
    length = int(SR * dur)
    x = chirp(180, 900, dur, 0.4) * env(length, 0.02, 0.65, 0.3, 0.15)
    squeak = chirp(600, 1400, dur * 0.8, 0.18)
    squeak = np.pad(squeak, (int(0.1 * SR), length - len(squeak) - int(0.1 * SR)))
    creak = lowpass(noise(dur, 0.15, 1), 500) * env(length, 0.02, 0.7, 0.2, 0.08)
    return layer(x, squeak, creak)


def projectile_release() -> np.ndarray:
    snap = noise(0.08, 0.9, 2) * env(int(SR * 0.08), 0.001, 0.05, 0.2, 0.2)
    thwack = tone(180, 0.12, 0.35) * env(int(SR * 0.12), 0.001, 0.08, 0.1, 0.4)
    whoosh = bandish_noise(0.18, 0.18, 3, 90) * env(int(SR * 0.18), 0.02, 0.2, 0.3, 0.3)
    return layer(snap, thwack, whoosh)


def stone_hit(strength: float, seed: int) -> np.ndarray:
    dur = 0.45
    body = tone(90 * strength, dur, 0.5) * env(int(SR * dur), 0.001, 0.08, 0.15, 0.5)
    click = noise(0.12, 0.28, seed) * env(int(SR * 0.12), 0.001, 0.05, 0.05, 0.3)
    return layer(body, click)


def blocks_falling() -> np.ndarray:
    out = np.zeros(int(SR * 1.8))
    for at, s, seed in [(0.0, 1.0, 4), (0.24, 0.9, 5), (0.47, 0.75, 6), (0.7, 0.65, 7), (1.0, 0.5, 8)]:
        out = place(out, stone_hit(s, seed), at)
    debris = bandish_noise(1.8, 0.12, 9, 40, 0.35) * env(len(out), 0.02, 0.4, 0.1, 0.25)
    return layer(out, debris)


def core_hit() -> np.ndarray:
    notes = [880, 1320, 1760]
    out = np.zeros(int(SR * 1.6))
    for i, f in enumerate(notes):
        bell = tone(f, 1.2, 0.24 / (i + 1)) * env(int(SR * 1.2), 0.001, 0.15, 0.25, 0.6)
        out = place(out, bell, i * 0.01)
    sparkle = chirp(2300, 2800, 0.22, 0.08)
    out = place(out, sparkle, 0.03)
    return out


def small_explosion() -> np.ndarray:
    pop = tone(140, 0.22, 0.55) * env(int(SR * 0.22), 0.001, 0.08, 0.08, 0.4)
    burst = bandish_noise(0.35, 0.55, 10, 120, 0.2) * env(int(SR * 0.35), 0.001, 0.12, 0.08, 0.45)
    return layer(pop, burst)


def big_explosion() -> np.ndarray:
    dur = 2.4
    body = tone(55, dur, 0.8) * env(int(SR * dur), 0.001, 0.08, 0.2, 0.6)
    sub = tone(35, dur, 0.55) * env(int(SR * dur), 0.001, 0.15, 0.18, 0.65)
    blast = bandish_noise(dur, 0.8, 11, 180, 0.25) * env(int(SR * dur), 0.001, 0.12, 0.15, 0.7)
    crumble = blocks_falling() * 0.35
    out = layer(body, sub, blast)
    out = place(out, crumble, 0.3)
    return out


def background_music() -> np.ndarray:
    dur = 16.0
    out = np.zeros(int(SR * dur))
    bpm = 112
    beat = 60.0 / bpm
    kick = tone(60, 0.18, 0.75) * env(int(SR * 0.18), 0.001, 0.08, 0.15, 0.5)
    click = bandish_noise(0.05, 0.25, 12, 30, 0.6) * env(int(SR * 0.05), 0.001, 0.04, 0.1, 0.2)
    melody = [523.25, 659.25, 783.99, 659.25, 587.33, 659.25, 783.99, 880.0]
    for bar in range(8):
        bar_start = bar * beat * 4
        for k in [0, 2]:
            out = place(out, kick, bar_start + k * beat)
        for k in [1, 3]:
            out = place(out, click, bar_start + k * beat)
        for step in range(8):
            note = melody[(bar + step) % len(melody)]
            pluck = layer(
                tone(note, 0.23, 0.18),
                np.pad(tone(note * 2, 0.18, 0.06), (0, int(SR * 0.23) - int(SR * 0.18))),
            ) * env(int(SR * 0.23), 0.001, 0.12, 0.12, 0.5)
            out = place(out, pluck, bar_start + step * (beat / 2))
        bass_note = [130.81, 146.83, 174.61, 146.83][bar % 4]
        bass = tone(bass_note, beat * 3.6, 0.16) * env(int(SR * beat * 3.6), 0.01, 0.2, 0.2, 0.3)
        out = place(out, bass, bar_start)
    return out


def ui_click() -> np.ndarray:
    click = tone(1900, 0.05, 0.35) * env(int(SR * 0.05), 0.001, 0.04, 0.06, 0.15)
    thock = tone(280, 0.07, 0.2) * env(int(SR * 0.07), 0.001, 0.04, 0.04, 0.2)
    return layer(click, thock)


def slow_motion_zoom() -> np.ndarray:
    dur = 1.8
    hum = chirp(110, 70, dur, 0.32) * env(int(SR * dur), 0.08, 0.25, 0.45, 0.25)
    whoosh = bandish_noise(dur, 0.25, 13, 80, 0.15) * env(int(SR * dur), 0.02, 0.3, 0.4, 0.2)
    return layer(hum, whoosh)


def points_increase() -> np.ndarray:
    out = np.zeros(int(SR * 1.6))
    freqs = [880, 988, 1175, 1319, 1568, 1760, 1976]
    t = 0.0
    for i, f in enumerate(freqs):
        ding = layer(
            tone(f, 0.14, 0.24),
            np.pad(tone(f * 2, 0.08, 0.07), (0, int(SR * 0.14) - int(SR * 0.08))),
        ) * env(int(SR * 0.14), 0.001, 0.08, 0.2, 0.4)
        out = place(out, ding, t)
        t += 0.11 - min(i, 5) * 0.008
    return out


def victory() -> np.ndarray:
    out = np.zeros(int(SR * 2.2))
    for at, freqs in [(0.0, [523.25, 659.25, 783.99]), (0.55, [587.33, 739.99, 880.0])]:
        chord = np.zeros(int(SR * 0.8))
        for f in freqs:
            chord += tone(f, 0.8, 0.16) * env(int(SR * 0.8), 0.001, 0.15, 0.25, 0.45)
        out = place(out, chord, at)
    return out


def unsuccessful() -> np.ndarray:
    out = np.zeros(int(SR * 1.1))
    slides = [(330, 250), (247, 196)]
    t = 0.0
    for a, b in slides:
        clip = chirp(a, b, 0.35, 0.28) * env(int(SR * 0.35), 0.001, 0.15, 0.2, 0.5)
        out = place(out, clip, t)
        t += 0.3
    out = place(out, tone(120, 0.18, 0.18) * env(int(SR * 0.18), 0.001, 0.1, 0.1, 0.4), 0.72)
    return out


def ticking_clock() -> np.ndarray:
    out = np.zeros(int(SR * 3.2))
    spacing = [0.65, 0.55, 0.45, 0.34, 0.25, 0.18]
    t = 0.0
    for i, s in enumerate(spacing):
        tick = layer(
            noise(0.025, 0.28, 20 + i) * env(int(SR * 0.025), 0.001, 0.04, 0.08, 0.1),
            tone(2400, 0.03, 0.08) * env(int(SR * 0.03), 0.001, 0.04, 0.08, 0.1),
        )
        out = place(out, tick, t)
        t += s
    return out


def bonus_powerup() -> np.ndarray:
    gliss = chirp(700, 1800, 0.5, 0.2) * env(int(SR * 0.5), 0.001, 0.2, 0.3, 0.3)
    sparkle = np.zeros(int(SR * 1.2))
    for i, f in enumerate([1320, 1760, 2093, 2637]):
        ding = tone(f, 0.22, 0.12) * env(int(SR * 0.22), 0.001, 0.12, 0.25, 0.45)
        sparkle = place(sparkle, ding, 0.18 + i * 0.08)
    return layer(np.pad(gliss, (0, len(sparkle) - len(gliss))), sparkle)


def main() -> None:
    os.makedirs(ASSET_DIR, exist_ok=True)
    renders = {
        "01_rubber_stretch.wav": rubber_stretch(),
        "02_projectile_release.wav": projectile_release(),
        "03_blocks_falling.wav": blocks_falling(),
        "04_core_hit.wav": core_hit(),
        "05_small_explosion.wav": small_explosion(),
        "06_big_explosion.wav": big_explosion(),
        "07_background_music_loop.wav": background_music(),
        "08_ui_button_click.wav": ui_click(),
        "09_slow_motion_zoom.wav": slow_motion_zoom(),
        "10_points_increase.wav": points_increase(),
        "11_victory_sound.wav": victory(),
        "12_unsuccessful_sound.wav": unsuccessful(),
        "13_clock_running_out.wav": ticking_clock(),
        "14_bonus_powerup.wav": bonus_powerup(),
    }
    for name, clip in renders.items():
        save(name, clip)
        print(f"wrote {name}")


if __name__ == "__main__":
    main()
