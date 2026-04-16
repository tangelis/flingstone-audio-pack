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


def harmonic_tone(
    freq: float,
    dur: float,
    amp: float = 1.0,
    partials: tuple[tuple[float, float], ...] = ((1.0, 1.0), (2.0, 0.35), (3.0, 0.18)),
    detune: float = 0.0,
) -> np.ndarray:
    out = np.zeros(int(SR * dur))
    for i, (mult, weight) in enumerate(partials):
        phase = i * 0.37
        out += tone(freq * (mult + detune), dur, amp * weight, phase)
        if detune:
            out += tone(freq * max(0.01, mult - detune), dur, amp * weight * 0.8, phase * 1.4)
    return out


def fm_tone(carrier: float, mod: float, index: float, dur: float, amp: float = 1.0) -> np.ndarray:
    t = np.arange(int(SR * dur)) / SR
    return amp * np.sin(2 * math.pi * carrier * t + index * np.sin(2 * math.pi * mod * t))


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


def highpass(x: np.ndarray, win: int = 300) -> np.ndarray:
    return x - lowpass(x, win)


def bandish_noise(dur: float, amp: float, seed: int, low_win: int, hi_mix: float = 0.0) -> np.ndarray:
    n = noise(dur, 1.0, seed)
    lp = lowpass(n, low_win)
    return amp * ((1 - hi_mix) * lp + hi_mix * n)


def saturate(x: np.ndarray, drive: float = 1.2) -> np.ndarray:
    return np.tanh(x * drive) / np.tanh(drive)


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


def room(x: np.ndarray, taps: tuple[tuple[float, float], ...] = ((0.021, 0.17), (0.047, 0.12), (0.083, 0.08))) -> np.ndarray:
    out = np.zeros(len(x) + int(max(delay for delay, _ in taps) * SR) + 1)
    source = lowpass(x, 180)
    for delay, gain in taps:
        i = int(delay * SR)
        out[i : i + len(source)] += source * gain
    return out


def echo(x: np.ndarray, delay: float = 0.16, feedback: float = 0.35, repeats: int = 3) -> np.ndarray:
    out = np.zeros(len(x) + int(delay * repeats * SR) + 1)
    gain = 1.0
    for repeat in range(repeats + 1):
        i = int(repeat * delay * SR)
        out[i : i + len(x)] += lowpass(x, 140 + repeat * 40) * gain
        gain *= feedback
    return out


def polish(x: np.ndarray, drive: float = 1.1, room_mix: float = 0.14, echo_mix: float = 0.0, air: float = 0.04) -> np.ndarray:
    out = x.copy()
    if room_mix:
        out = layer(out, room(x) * room_mix)
    if echo_mix:
        out = layer(out, echo(x) * echo_mix)
    if air:
        out = layer(out, highpass(out, 150) * air)
    return saturate(out, drive)


def stutter(x: np.ndarray, slices: int = 6, decay: float = 0.82, spacing: float = 0.035) -> np.ndarray:
    if len(x) == 0 or slices <= 1:
        return x
    take = max(1, len(x) // max(4, slices))
    snippet = x[:take]
    out = np.zeros(len(x) + int((slices - 1) * spacing * SR) + 1)
    for i in range(slices):
        at = int(i * spacing * SR)
        gain = decay**i
        out[at : at + len(snippet)] += lowpass(snippet, 90 + i * 18) * gain
    return out


def ring(freqs: list[float], dur: float, amp: float = 0.2, shimmer: float = 0.0) -> np.ndarray:
    out = np.zeros(int(SR * dur))
    for i, f in enumerate(freqs):
        clip = harmonic_tone(
            f,
            dur,
            amp / (1 + i * 0.35),
            partials=((1.0, 1.0), (2.0, 0.22), (3.01, 0.11), (4.32, 0.06)),
            detune=0.0015,
        )
        clip *= env(len(clip), 0.001, 0.18, 0.2, 0.62)
        out += clip
    if shimmer:
        shimmer_clip = chirp(max(freqs) * 1.08, max(freqs) * 1.24, min(dur, 0.28), shimmer)
        out = layer(out, np.pad(shimmer_clip, (0, len(out) - len(shimmer_clip))))
    return polish(out, drive=1.05, room_mix=0.18, air=0.03)


def impact(freq: float, dur: float, amp: float, seed: int, grit: float = 0.18, body_harmonics: tuple[tuple[float, float], ...] = ((1.0, 1.0), (1.98, 0.3))) -> np.ndarray:
    body = harmonic_tone(freq, dur, amp, body_harmonics, detune=0.003) * env(int(SR * dur), 0.001, 0.08, 0.12, 0.5)
    grit_layer = highpass(noise(min(dur, 0.18), grit, seed), 70) * env(int(SR * min(dur, 0.18)), 0.001, 0.05, 0.05, 0.25)
    return layer(body, grit_layer)


def whoosh(dur: float, start: float, end: float, amp: float, seed: int, airy: float = 0.18) -> np.ndarray:
    air = bandish_noise(dur, airy, seed, 90, 0.24) * env(int(SR * dur), 0.02, 0.25, 0.24, 0.18)
    sweep = chirp(start, end, dur, amp) * env(int(SR * dur), 0.01, 0.2, 0.24, 0.22)
    return layer(air, sweep)


def pluck(freq: float, dur: float, amp: float = 0.18) -> np.ndarray:
    clip = harmonic_tone(freq, dur, amp, partials=((1.0, 1.0), (2.0, 0.28), (3.0, 0.1), (4.0, 0.05)), detune=0.002)
    click = highpass(noise(0.012, amp * 0.18, int(freq)), 180)
    return polish(layer(clip * env(len(clip), 0.001, 0.1, 0.12, 0.34), click), drive=1.02, room_mix=0.07, air=0.03)


def mallet(freq: float, dur: float, amp: float = 0.18) -> np.ndarray:
    clip = harmonic_tone(freq, dur, amp, partials=((1.0, 1.0), (3.0, 0.22), (4.0, 0.08), (5.0, 0.04)), detune=0.001)
    knock = lowpass(noise(0.015, amp * 0.22, int(freq) + 9), 36)
    return polish(layer(clip * env(len(clip), 0.001, 0.08, 0.1, 0.3), knock), drive=1.03, room_mix=0.08, air=0.02)


def sub_boom(freq: float, dur: float, amp: float) -> np.ndarray:
    return harmonic_tone(freq, dur, amp, partials=((1.0, 1.0), (2.0, 0.2)), detune=0.002) * env(int(SR * dur), 0.001, 0.12, 0.14, 0.64)


def rubber_stretch_a() -> np.ndarray:
    dur = 1.22
    length = int(SR * dur)
    pull = chirp(175, 920, dur, 0.34) * env(length, 0.02, 0.62, 0.22, 0.14)
    squeak = harmonic_tone(780, dur * 0.76, 0.11, partials=((1.0, 1.0), (2.0, 0.16), (2.98, 0.05)), detune=0.008)
    squeak = np.pad(squeak, (int(0.11 * SR), length - len(squeak) - int(0.11 * SR)))
    cloth = lowpass(noise(dur, 0.1, 1), 520) * env(length, 0.04, 0.62, 0.08, 0.1)
    return polish(layer(pull, squeak, cloth), drive=1.06, room_mix=0.08, air=0.02)


def rubber_stretch_b() -> np.ndarray:
    dur = 1.0
    length = int(SR * dur)
    bwoing = fm_tone(160, 11, 8.5, dur * 0.78, 0.24) * env(int(SR * dur * 0.78), 0.01, 0.46, 0.16, 0.22)
    bend = chirp(170, 1080, dur * 0.72, 0.18) * env(int(SR * dur * 0.72), 0.01, 0.4, 0.2, 0.2)
    balloon = highpass(noise(dur * 0.58, 0.13, 2), 210) * env(int(SR * dur * 0.58), 0.02, 0.48, 0.1, 0.22)
    stretch = np.pad(layer(bwoing, bend), (0, length - len(bwoing)))
    balloon = np.pad(balloon, (int(0.12 * SR), length - len(balloon) - int(0.12 * SR)))
    return polish(layer(stretch, balloon), drive=1.12, room_mix=0.12, echo_mix=0.02, air=0.03)


def rubber_stretch_c() -> np.ndarray:
    dur = 1.28
    length = int(SR * dur)
    tension = harmonic_tone(140, dur, 0.2, partials=((1.0, 1.0), (1.5, 0.22), (2.0, 0.14)), detune=0.006)
    tension *= env(length, 0.05, 0.48, 0.24, 0.16)
    whine = chirp(420, 1450, dur * 0.82, 0.14) * env(int(SR * dur * 0.82), 0.03, 0.55, 0.14, 0.16)
    whine = np.pad(whine, (int(0.08 * SR), length - len(whine) - int(0.08 * SR)))
    creak = highpass(lowpass(noise(dur, 0.16, 3), 420), 28) * env(length, 0.04, 0.6, 0.08, 0.18)
    return polish(layer(tension, whine, creak), drive=1.1, room_mix=0.18, echo_mix=0.03, air=0.04)


def projectile_release_a() -> np.ndarray:
    snap = highpass(noise(0.065, 0.92, 4), 120) * env(int(SR * 0.065), 0.001, 0.04, 0.18, 0.16)
    thwack = harmonic_tone(185, 0.11, 0.24, partials=((1.0, 1.0), (2.0, 0.18)), detune=0.004) * env(int(SR * 0.11), 0.001, 0.08, 0.08, 0.34)
    air = whoosh(0.16, 980, 340, 0.08, 5, 0.14)
    return polish(layer(snap, thwack, air), drive=1.14, room_mix=0.08, air=0.04)


def projectile_release_b() -> np.ndarray:
    crack = highpass(noise(0.085, 1.0, 6), 65) * env(int(SR * 0.085), 0.001, 0.03, 0.12, 0.18)
    pocket = harmonic_tone(134, 0.12, 0.21, partials=((1.0, 1.0), (1.97, 0.22)), detune=0.006) * env(int(SR * 0.12), 0.001, 0.06, 0.08, 0.26)
    ringoff = ring([1730, 2070, 2460], 0.22, 0.065, 0.025)
    ringoff = np.pad(ringoff, (int(0.018 * SR), 0))
    return polish(layer(crack, pocket, ringoff), drive=1.16, room_mix=0.1, air=0.04)


def projectile_release_c() -> np.ndarray:
    whip = chirp(2200, 180, 0.22, 0.12) * env(int(SR * 0.22), 0.001, 0.08, 0.04, 0.22)
    launch = highpass(noise(0.05, 0.8, 7), 180) * env(int(SR * 0.05), 0.001, 0.03, 0.08, 0.12)
    trail = whoosh(0.24, 1200, 320, 0.1, 8, 0.16)
    ping = ring([920, 1370], 0.12, 0.05, 0.02)
    return polish(layer(launch, whip, trail, np.pad(ping, (int(0.04 * SR), 0))), drive=1.12, room_mix=0.12, echo_mix=0.02, air=0.04)


def blocks_falling_a() -> np.ndarray:
    out = np.zeros(int(SR * 1.95))
    for at, freq, seed in [(0.0, 86, 9), (0.24, 79, 10), (0.47, 73, 11), (0.72, 68, 12), (1.05, 61, 13)]:
        out = place(out, impact(freq, 0.46, 0.4, seed, 0.12), at)
    debris = bandish_noise(1.95, 0.12, 14, 46, 0.2) * env(len(out), 0.02, 0.4, 0.08, 0.24)
    rumble = sub_boom(43, 1.3, 0.08)
    return polish(layer(out, debris, np.pad(rumble, (int(0.1 * SR), len(out) - len(rumble) - int(0.1 * SR)))), drive=1.08, room_mix=0.16, air=0.02)


def blocks_falling_b() -> np.ndarray:
    out = np.zeros(int(SR * 1.45))
    for at, freq, seed in [(0.0, 64, 15), (0.18, 60, 16), (0.36, 56, 17), (0.54, 52, 18)]:
        out = place(out, impact(freq, 0.32, 0.54, seed, 0.18, ((1.0, 1.0), (1.5, 0.14), (2.0, 0.22))), at)
    crunch = highpass(noise(0.4, 0.12, 19), 120) * env(int(SR * 0.4), 0.02, 0.3, 0.06, 0.18)
    return polish(place(out, crunch, 0.42), drive=1.14, room_mix=0.1, air=0.05)


def blocks_falling_c() -> np.ndarray:
    out = np.zeros(int(SR * 2.2))
    for at, freq, seed in [(0.0, 92, 20), (0.31, 82, 21), (0.63, 71, 22), (1.02, 60, 23)]:
        out = place(out, impact(freq, 0.58, 0.48, seed, 0.14, ((1.0, 1.0), (1.8, 0.2), (2.4, 0.09))), at)
    long_rumble = sub_boom(36, 1.8, 0.12)
    grit = bandish_noise(2.2, 0.16, 24, 70, 0.2) * env(len(out), 0.02, 0.55, 0.08, 0.3)
    return polish(layer(out, long_rumble, grit), drive=1.1, room_mix=0.22, air=0.03)


def core_hit_a() -> np.ndarray:
    return ring([880, 1320, 1760, 2200], 1.5, 0.22, 0.05)


def core_hit_b() -> np.ndarray:
    ping = ring([640, 973, 1280], 1.25, 0.2, 0.025)
    metal = highpass(noise(0.08, 0.11, 25), 120) * env(int(SR * 0.08), 0.001, 0.06, 0.08, 0.2)
    return polish(layer(ping, metal), drive=1.08, room_mix=0.18, air=0.03)


def core_hit_c() -> np.ndarray:
    prism = ring([700, 1050, 1575], 1.3, 0.18, 0.035)
    charged = fm_tone(260, 39, 6.5, 0.38, 0.12) * env(int(SR * 0.38), 0.001, 0.12, 0.12, 0.34)
    pulse = sub_boom(60, 0.4, 0.08)
    return polish(layer(prism, np.pad(charged, (int(0.02 * SR), 0)), np.pad(pulse, (int(0.03 * SR), 0))), drive=1.12, room_mix=0.24, echo_mix=0.03, air=0.04)


def small_explosion_a() -> np.ndarray:
    pop = harmonic_tone(150, 0.2, 0.26, partials=((1.0, 1.0), (2.0, 0.18)), detune=0.004) * env(int(SR * 0.2), 0.001, 0.06, 0.07, 0.35)
    air = bandish_noise(0.28, 0.32, 26, 160, 0.06) * env(int(SR * 0.28), 0.001, 0.08, 0.06, 0.25)
    pebbles = highpass(noise(0.14, 0.07, 27), 200) * env(int(SR * 0.14), 0.001, 0.04, 0.03, 0.2)
    return polish(layer(pop, air, np.pad(pebbles, (int(0.04 * SR), 0))), drive=1.12, room_mix=0.08, air=0.04)


def small_explosion_b() -> np.ndarray:
    boom = sub_boom(94, 0.34, 0.32)
    dust = bandish_noise(0.4, 0.52, 28, 220, 0.12) * env(int(SR * 0.4), 0.001, 0.12, 0.08, 0.38)
    return polish(layer(boom, dust), drive=1.14, room_mix=0.12, air=0.03)


def small_explosion_c() -> np.ndarray:
    burst = highpass(noise(0.05, 0.85, 29), 140) * env(int(SR * 0.05), 0.001, 0.03, 0.08, 0.12)
    shock = chirp(400, 90, 0.18, 0.16) * env(int(SR * 0.18), 0.001, 0.08, 0.08, 0.24)
    sparkle = ring([1200, 1700, 2200], 0.22, 0.05, 0.025)
    dust = bandish_noise(0.26, 0.2, 30, 100, 0.18) * env(int(SR * 0.26), 0.001, 0.1, 0.08, 0.2)
    return polish(layer(burst, shock, np.pad(sparkle, (int(0.02 * SR), 0)), dust), drive=1.1, room_mix=0.12, air=0.05)


def big_explosion_a() -> np.ndarray:
    dur = 2.6
    body = sub_boom(54, dur, 0.38)
    sub = sub_boom(32, dur, 0.22)
    blast = bandish_noise(dur, 0.64, 31, 190, 0.16) * env(int(SR * dur), 0.001, 0.1, 0.12, 0.72)
    crumble = blocks_falling_a() * 0.32
    return polish(place(layer(body, sub, blast), crumble, 0.36), drive=1.14, room_mix=0.22, air=0.03)


def big_explosion_b() -> np.ndarray:
    dur = 2.35
    slam = harmonic_tone(70, dur, 0.46, partials=((1.0, 1.0), (1.45, 0.2), (2.0, 0.16)), detune=0.005) * env(int(SR * dur), 0.001, 0.06, 0.15, 0.55)
    debris = highpass(noise(dur, 0.4, 32), 90) * env(int(SR * dur), 0.001, 0.08, 0.11, 0.6)
    air = chirp(420, 180, 0.45, 0.14)
    return polish(layer(slam, debris, np.pad(air, (int(0.05 * SR), int(SR * dur) - len(air) - int(0.05 * SR)))), drive=1.16, room_mix=0.18, echo_mix=0.03, air=0.05)


def big_explosion_c() -> np.ndarray:
    dur = 2.8
    rupture = sub_boom(48, dur, 0.42)
    pressure = chirp(260, 50, 0.85, 0.12) * env(int(SR * 0.85), 0.001, 0.18, 0.2, 0.34)
    grit = bandish_noise(dur, 0.62, 33, 150, 0.26) * env(int(SR * dur), 0.001, 0.12, 0.1, 0.68)
    debris = blocks_falling_c() * 0.28
    return polish(place(layer(rupture, pressure, grit), debris, 0.28), drive=1.12, room_mix=0.26, echo_mix=0.03, air=0.03)


def background_music_a() -> np.ndarray:
    dur = 16.0
    out = np.zeros(int(SR * dur))
    bpm = 112
    beat = 60.0 / bpm
    kick = sub_boom(60, 0.18, 0.34)
    clap = highpass(noise(0.06, 0.18, 34), 120) * env(int(SR * 0.06), 0.001, 0.04, 0.06, 0.18)
    melody = [523.25, 659.25, 783.99, 659.25, 587.33, 659.25, 783.99, 880.0]
    for bar in range(8):
        bar_start = bar * beat * 4
        for k in [0, 2]:
            out = place(out, kick, bar_start + k * beat)
        for k in [1, 3]:
            out = place(out, clap, bar_start + k * beat)
        for step in range(8):
            note = melody[(bar + step) % len(melody)]
            out = place(out, mallet(note, 0.23, 0.15), bar_start + step * (beat / 2))
        bass_note = [130.81, 146.83, 174.61, 146.83][bar % 4]
        bass = harmonic_tone(bass_note, beat * 3.5, 0.11, partials=((1.0, 1.0), (2.0, 0.12)), detune=0.001)
        bass *= env(len(bass), 0.01, 0.18, 0.18, 0.24)
        out = place(out, bass, bar_start)
    return polish(out, drive=1.06, room_mix=0.08, air=0.03)


def background_music_b() -> np.ndarray:
    dur = 16.0
    out = np.zeros(int(SR * dur))
    bpm = 124
    beat = 60.0 / bpm
    pizz_seq = [659.25, 783.99, 880.0, 987.77, 880.0, 783.99, 739.99, 659.25]
    horn_chords = [[392.0, 493.88], [440.0, 554.37], [493.88, 659.25], [440.0, 554.37]]
    for bar in range(8):
        start = bar * beat * 4
        for step in range(8):
            out = place(out, pluck(pizz_seq[(bar + step) % len(pizz_seq)], 0.14, 0.12), start + step * (beat / 2))
        chord = ring(horn_chords[bar % 4], 0.42, 0.09, 0.01)
        out = place(out, chord, start + beat * 2.8)
        out = place(out, highpass(noise(0.05, 0.06, 40 + bar), 170) * env(int(SR * 0.05), 0.001, 0.04, 0.04, 0.12), start + beat * 1.5)
    bass = harmonic_tone(196.0, dur, 0.04, partials=((1.0, 1.0), (2.0, 0.1)), detune=0.001) * env(int(SR * dur), 0.01, 0.2, 0.18, 0.2)
    return polish(layer(out, bass), drive=1.05, room_mix=0.1, air=0.03)


def background_music_c() -> np.ndarray:
    dur = 16.0
    out = np.zeros(int(SR * dur))
    bpm = 118
    beat = 60.0 / bpm
    motif = [392.0, 523.25, 659.25, 783.99, 659.25, 523.25, 440.0, 493.88]
    for bar in range(8):
        start = bar * beat * 4
        out = place(out, sub_boom(56, 0.2, 0.26), start)
        out = place(out, highpass(noise(0.05, 0.12, 60 + bar), 110) * env(int(SR * 0.05), 0.001, 0.03, 0.04, 0.14), start + beat * 2)
        for step in range(8):
            note = motif[(bar + step) % len(motif)]
            out = place(out, layer(pluck(note, 0.18, 0.12), mallet(note * 0.5, 0.18, 0.05)), start + step * (beat / 2))
        chord = ring([261.63, 392.0, 523.25], 0.6, 0.08, 0.015)
        out = place(out, chord, start + beat * 2.5)
    pulse = harmonic_tone(98.0, dur, 0.05, partials=((1.0, 1.0), (2.0, 0.08)), detune=0.0007) * env(int(SR * dur), 0.01, 0.16, 0.18, 0.18)
    return polish(layer(out, pulse), drive=1.05, room_mix=0.12, echo_mix=0.01, air=0.03)


def ui_click_a() -> np.ndarray:
    click = ring([1800, 2400], 0.06, 0.12, 0.02)
    glass = chirp(2600, 3400, 0.02, 0.04)
    return polish(layer(click, glass), drive=1.04, room_mix=0.05, air=0.04)


def ui_click_b() -> np.ndarray:
    thock = harmonic_tone(240, 0.08, 0.14, partials=((1.0, 1.0), (2.0, 0.12)), detune=0.006) * env(int(SR * 0.08), 0.001, 0.04, 0.04, 0.2)
    spring = chirp(620, 980, 0.035, 0.08)
    spring = np.pad(spring, (int(0.012 * SR), 0))
    return polish(layer(thock, spring), drive=1.06, room_mix=0.04, air=0.03)


def ui_click_c() -> np.ndarray:
    gem = ring([1420, 1980, 2640], 0.08, 0.07, 0.025)
    tick = highpass(noise(0.012, 0.14, 71), 240) * env(int(SR * 0.012), 0.001, 0.02, 0.02, 0.08)
    return polish(layer(gem, tick), drive=1.03, room_mix=0.06, air=0.05)


def slow_motion_zoom_a() -> np.ndarray:
    dur = 1.8
    hum = harmonic_tone(110, dur, 0.18, partials=((1.0, 1.0), (2.0, 0.16)), detune=0.002) * env(int(SR * dur), 0.08, 0.24, 0.42, 0.25)
    whoosh_layer = whoosh(dur, 420, 90, 0.08, 72, 0.18)
    return polish(layer(hum, whoosh_layer), drive=1.06, room_mix=0.18, air=0.03)


def slow_motion_zoom_b() -> np.ndarray:
    dur = 1.9
    shear = chirp(220, 960, dur * 0.8, 0.18) * env(int(SR * dur * 0.8), 0.03, 0.35, 0.15, 0.22)
    tape = lowpass(noise(dur, 0.08, 73), 260) * env(int(SR * dur), 0.02, 0.45, 0.1, 0.24)
    pulse = sub_boom(42, dur, 0.08)
    return polish(layer(shear, tape, pulse), drive=1.08, room_mix=0.2, echo_mix=0.03, air=0.04)


def slow_motion_zoom_c() -> np.ndarray:
    dur = 2.0
    warp = fm_tone(145, 27, 6.8, dur, 0.15) * env(int(SR * dur), 0.05, 0.28, 0.2, 0.24)
    air = whoosh(dur, 680, 110, 0.08, 74, 0.18)
    halo = ring([520, 780], 0.8, 0.05, 0.02)
    return polish(layer(warp, air, np.pad(halo, (int(0.3 * SR), 0))), drive=1.08, room_mix=0.22, echo_mix=0.03, air=0.04)


def points_increase_a() -> np.ndarray:
    out = np.zeros(int(SR * 1.7))
    freqs = [880, 988, 1175, 1319, 1568, 1760, 1976]
    t = 0.0
    for i, f in enumerate(freqs):
        out = place(out, ring([f, f * 2], 0.15, 0.11, 0.01), t)
        t += 0.11 - min(i, 5) * 0.008
    return polish(out, drive=1.04, room_mix=0.08, air=0.05)


def points_increase_b() -> np.ndarray:
    out = np.zeros(int(SR * 1.7))
    freqs = [660, 740, 830, 990, 1180]
    t = 0.0
    for i in range(9):
        f = freqs[i % len(freqs)]
        tick = harmonic_tone(f, 0.07, 0.1, partials=((1.0, 1.0), (2.0, 0.16)), detune=0.002) * env(int(SR * 0.07), 0.001, 0.04, 0.05, 0.16)
        if i in (3, 6, 8):
            tick = layer(tick, ring([f * 2, f * 3], 0.13, 0.05, 0.02))
        out = place(out, tick, t)
        t += 0.15
    return polish(out, drive=1.05, room_mix=0.08, air=0.05)


def points_increase_c() -> np.ndarray:
    out = np.zeros(int(SR * 2.0))
    freqs = [740, 880, 1047, 1319, 1568, 1760]
    t = 0.0
    for i, f in enumerate(freqs):
        out = place(out, ring([f, f * 1.5, f * 2], 0.18, 0.07, 0.025), t)
        if i >= 3:
            out = place(out, highpass(noise(0.03, 0.04, 80 + i), 210) * env(int(SR * 0.03), 0.001, 0.02, 0.03, 0.08), t)
        t += 0.16 - i * 0.012
    return polish(out, drive=1.03, room_mix=0.12, echo_mix=0.02, air=0.05)


def victory_a() -> np.ndarray:
    out = np.zeros(int(SR * 2.0))
    for at, freqs in [(0.0, [523.25, 659.25, 783.99]), (0.52, [659.25, 783.99, 987.77])]:
        out = place(out, ring(freqs, 0.75, 0.15, 0.02), at)
    sparkle = ring([1760, 2093], 0.3, 0.05, 0.03)
    return polish(place(out, sparkle, 1.1), drive=1.06, room_mix=0.18, air=0.04)


def victory_b() -> np.ndarray:
    chimes = ring([1175, 1568, 2093], 0.45, 0.1, 0.03)
    horn = ring([523.25, 659.25, 783.99], 1.1, 0.11, 0.01)
    return polish(layer(chimes, np.pad(horn, (int(0.15 * SR), 0))), drive=1.06, room_mix=0.2, air=0.04)


def victory_c() -> np.ndarray:
    crown = ring([659.25, 880.0, 1175.0], 0.52, 0.1, 0.03)
    lift = harmonic_tone(392.0, 1.2, 0.12, partials=((1.0, 1.0), (2.0, 0.18), (3.0, 0.08)), detune=0.001)
    lift *= env(len(lift), 0.01, 0.18, 0.2, 0.28)
    tail = ring([1760, 2350], 0.32, 0.04, 0.03)
    return polish(layer(crown, np.pad(lift, (int(0.12 * SR), 0)), np.pad(tail, (int(0.82 * SR), 0))), drive=1.05, room_mix=0.22, echo_mix=0.03, air=0.05)


def unsuccessful_a() -> np.ndarray:
    out = np.zeros(int(SR * 1.05))
    for i, (a, b) in enumerate([(370, 280), (294, 220)]):
        clip = chirp(a, b, 0.3, 0.25) * env(int(SR * 0.3), 0.001, 0.12, 0.16, 0.46)
        out = place(out, clip, i * 0.28)
    return polish(out, drive=1.02, room_mix=0.1, air=0.02)


def unsuccessful_b() -> np.ndarray:
    whistle = chirp(620, 210, 0.52, 0.16) * env(int(SR * 0.52), 0.01, 0.22, 0.12, 0.32)
    thud = harmonic_tone(118, 0.14, 0.1, partials=((1.0, 1.0), (2.0, 0.1)), detune=0.004) * env(int(SR * 0.14), 0.001, 0.06, 0.06, 0.22)
    return polish(layer(whistle, np.pad(thud, (int(0.48 * SR), 0))), drive=1.03, room_mix=0.08, air=0.02)


def unsuccessful_c() -> np.ndarray:
    clonk = impact(210, 0.16, 0.15, 90, 0.08, ((1.0, 1.0), (1.33, 0.18), (2.1, 0.08)))
    sigh = chirp(300, 180, 0.4, 0.1) * env(int(SR * 0.4), 0.03, 0.2, 0.1, 0.3)
    return polish(layer(clonk, np.pad(sigh, (int(0.12 * SR), 0))), drive=1.02, room_mix=0.1, air=0.02)


def ticking_clock_a() -> np.ndarray:
    out = np.zeros(int(SR * 3.4))
    spacing = [0.7, 0.6, 0.5, 0.38, 0.28, 0.2]
    t = 0.0
    for i, s in enumerate(spacing):
        tick = layer(
            noise(0.026, 0.16, 91 + i) * env(int(SR * 0.026), 0.001, 0.04, 0.08, 0.08),
            tone(1600, 0.03, 0.05) * env(int(SR * 0.03), 0.001, 0.04, 0.06, 0.08),
        )
        out = place(out, tick, t)
        t += s
    pad = harmonic_tone(90, 1.2, 0.05, partials=((1.0, 1.0), (2.0, 0.12)), detune=0.001) * env(int(SR * 1.2), 0.08, 0.2, 0.15, 0.28)
    return polish(place(out, pad, 2.1), drive=1.02, room_mix=0.08, air=0.03)


def ticking_clock_b() -> np.ndarray:
    out = np.zeros(int(SR * 2.7))
    spacing = [0.42, 0.34, 0.28, 0.22, 0.16, 0.12, 0.09]
    t = 0.0
    for i, s in enumerate(spacing):
        tick = layer(
            tone(2200, 0.028, 0.08) * env(int(SR * 0.028), 0.001, 0.03, 0.04, 0.06),
            highpass(noise(0.022, 0.08, 100 + i), 170) * env(int(SR * 0.022), 0.001, 0.03, 0.04, 0.06),
        )
        out = place(out, tick, t)
        t += s
    pulse = tone(2600, 0.5, 0.03) * env(int(SR * 0.5), 0.1, 0.3, 0.2, 0.2)
    return polish(place(out, pulse, 1.8), drive=1.03, room_mix=0.1, air=0.04)


def ticking_clock_c() -> np.ndarray:
    out = np.zeros(int(SR * 3.1))
    spacing = [0.55, 0.46, 0.36, 0.28, 0.2, 0.15, 0.11]
    t = 0.0
    for i, s in enumerate(spacing):
        tick = layer(
            highpass(noise(0.022, 0.1, 110 + i), 180) * env(int(SR * 0.022), 0.001, 0.03, 0.04, 0.06),
            tone(1800 + i * 60, 0.028, 0.05) * env(int(SR * 0.028), 0.001, 0.03, 0.04, 0.06),
        )
        out = place(out, tick, t)
        t += s
    heart = sub_boom(52, 1.1, 0.06)
    out = place(out, heart, 1.8)
    return polish(out, drive=1.04, room_mix=0.14, air=0.03)


def bonus_powerup_a() -> np.ndarray:
    gliss = chirp(700, 1850, 0.5, 0.18) * env(int(SR * 0.5), 0.001, 0.18, 0.22, 0.28)
    sparkle = ring([1320, 1760, 2093, 2637], 1.0, 0.08, 0.05)
    return polish(layer(np.pad(gliss, (0, len(sparkle) - len(gliss))), sparkle), drive=1.04, room_mix=0.18, air=0.05)


def bonus_powerup_b() -> np.ndarray:
    zip_in = chirp(280, 980, 0.28, 0.2) * env(int(SR * 0.28), 0.001, 0.08, 0.12, 0.18)
    swell = ring([392, 523.25, 659.25], 0.9, 0.12, 0.02)
    coin = ring([1568, 2093], 0.18, 0.07, 0.03)
    out = layer(np.pad(zip_in, (0, len(swell) - len(zip_in))), swell)
    return polish(place(out, coin, 0.58), drive=1.04, room_mix=0.18, air=0.05)


def bonus_powerup_c() -> np.ndarray:
    lift = ring([784, 1047, 1397], 0.26, 0.08, 0.02)
    bloom = ring([523.25, 783.99, 1175], 1.1, 0.09, 0.04)
    streak = whoosh(0.36, 1500, 620, 0.08, 120, 0.14)
    return polish(layer(lift, np.pad(streak, (int(0.05 * SR), 0)), np.pad(bloom, (int(0.18 * SR), 0))), drive=1.04, room_mix=0.22, echo_mix=0.03, air=0.05)


def rubber_stretch_d() -> np.ndarray:
    dur = 1.34
    length = int(SR * dur)
    bend = fm_tone(120, 7, 8.8, dur, 0.14) * env(length, 0.04, 0.52, 0.18, 0.18)
    whine = chirp(280, 1380, dur * 0.8, 0.12) * env(int(SR * dur * 0.8), 0.03, 0.4, 0.14, 0.18)
    grit = highpass(lowpass(noise(dur, 0.14, 130), 280), 26) * env(length, 0.03, 0.6, 0.08, 0.16)
    whine = np.pad(whine, (int(0.09 * SR), length - len(whine) - int(0.09 * SR)))
    return polish(layer(bend, whine, grit), drive=1.12, room_mix=0.22, echo_mix=0.05, air=0.05)


def projectile_release_d() -> np.ndarray:
    snap = highpass(noise(0.045, 0.95, 131), 180) * env(int(SR * 0.045), 0.001, 0.02, 0.06, 0.09)
    zap = chirp(2200, 240, 0.16, 0.12) * env(int(SR * 0.16), 0.001, 0.06, 0.05, 0.16)
    tail = fm_tone(240, 31, 6.0, 0.22, 0.08) * env(int(SR * 0.22), 0.01, 0.14, 0.08, 0.22)
    return polish(layer(snap, zap, np.pad(tail, (int(0.03 * SR), 0))), drive=1.14, room_mix=0.12, echo_mix=0.04, air=0.05)


def blocks_falling_d() -> np.ndarray:
    out = np.zeros(int(SR * 1.95))
    for at, freq, seed in [(0.0, 94, 132), (0.17, 72, 133), (0.39, 88, 134), (0.68, 61, 135), (1.05, 48, 136)]:
        clip = impact(freq, 0.24, 0.34, seed, 0.18, ((1.0, 1.0), (1.31, 0.18), (2.0, 0.16)))
        out = place(out, stutter(clip, 3, 0.78, 0.018), at)
    machine = fm_tone(68, 14, 5.8, 1.4, 0.06) * env(int(SR * 1.4), 0.02, 0.24, 0.1, 0.18)
    return polish(layer(out, np.pad(machine, (int(0.2 * SR), len(out) - len(machine) - int(0.2 * SR)))), drive=1.1, room_mix=0.18, echo_mix=0.03, air=0.04)


def core_hit_d() -> np.ndarray:
    cluster = ring([512, 777, 1040, 1333], 1.26, 0.16, 0.035)
    glitch = stutter(fm_tone(310, 43, 7.4, 0.28, 0.1) * env(int(SR * 0.28), 0.001, 0.12, 0.08, 0.16), 4, 0.74, 0.024)
    sub = sub_boom(76, 0.28, 0.06)
    return polish(layer(cluster, np.pad(glitch, (int(0.025 * SR), 0)), np.pad(sub, (int(0.03 * SR), 0))), drive=1.08, room_mix=0.26, echo_mix=0.04, air=0.05)


def small_explosion_d() -> np.ndarray:
    crack = highpass(noise(0.03, 0.88, 137), 220) * env(int(SR * 0.03), 0.001, 0.02, 0.05, 0.06)
    burst = stutter(chirp(900, 130, 0.16, 0.13) * env(int(SR * 0.16), 0.001, 0.08, 0.06, 0.12), 4, 0.72, 0.02)
    dust = bandish_noise(0.24, 0.16, 138, 90, 0.22) * env(int(SR * 0.24), 0.001, 0.1, 0.08, 0.2)
    return polish(layer(crack, burst, dust), drive=1.12, room_mix=0.14, echo_mix=0.03, air=0.05)


def big_explosion_d() -> np.ndarray:
    dur = 2.7
    body = sub_boom(46, dur, 0.34)
    rupture = stutter(chirp(420, 60, 0.62, 0.16) * env(int(SR * 0.62), 0.001, 0.14, 0.08, 0.22), 5, 0.8, 0.028)
    grit = bandish_noise(dur, 0.48, 139, 120, 0.28) * env(int(SR * dur), 0.001, 0.12, 0.08, 0.66)
    debris = blocks_falling_d() * 0.28
    return polish(place(layer(body, rupture, grit), debris, 0.26), drive=1.12, room_mix=0.28, echo_mix=0.04, air=0.04)


def background_music_d() -> np.ndarray:
    dur = 16.0
    out = np.zeros(int(SR * dur))
    bpm = 136
    beat = 60.0 / bpm
    bassline = [65.41, 82.41, 92.5, 87.31, 73.42, 98.0, 82.41, 65.41]
    motif = [523.25, 659.25, 493.88, 739.99, 587.33, 783.99, 659.25, 392.0]
    for bar in range(8):
        start = bar * beat * 4
        kick = sub_boom(52 + (bar % 2) * 4, 0.14, 0.22)
        out = place(out, kick, start)
        out = place(out, highpass(noise(0.03, 0.11, 140 + bar), 160) * env(int(SR * 0.03), 0.001, 0.02, 0.03, 0.08), start + beat * 1.5)
        out = place(out, highpass(noise(0.03, 0.08, 160 + bar), 190) * env(int(SR * 0.03), 0.001, 0.02, 0.03, 0.08), start + beat * 3.0)
        for step in range(8):
            note = motif[(bar + step) % len(motif)]
            pl = pluck(note, 0.13, 0.09)
            gl = stutter(pl * 0.55, 2, 0.7, 0.012)
            out = place(out, layer(pl, gl), start + step * (beat / 2))
        bass = harmonic_tone(bassline[bar % len(bassline)], beat * 3.7, 0.08, partials=((1.0, 1.0), (2.0, 0.14), (3.0, 0.05)), detune=0.002)
        bass *= env(len(bass), 0.01, 0.14, 0.15, 0.22)
        out = place(out, bass, start)
    haze = fm_tone(220, 0.42, 3.2, dur, 0.02) * env(int(SR * dur), 0.08, 0.2, 0.08, 0.16)
    return polish(layer(out, haze), drive=1.04, room_mix=0.08, echo_mix=0.04, air=0.04)


def ui_click_d() -> np.ndarray:
    tick = highpass(noise(0.01, 0.18, 180), 260) * env(int(SR * 0.01), 0.001, 0.02, 0.02, 0.06)
    ringy = ring([1320, 1870, 2450], 0.07, 0.05, 0.025)
    return polish(layer(tick, stutter(ringy * 0.6, 2, 0.65, 0.01)), drive=1.02, room_mix=0.06, air=0.05)


def slow_motion_zoom_d() -> np.ndarray:
    dur = 2.1
    warp = fm_tone(132, 17, 7.2, dur, 0.12) * env(int(SR * dur), 0.05, 0.24, 0.18, 0.24)
    sweep = stutter(whoosh(dur, 820, 140, 0.08, 181, 0.16), 3, 0.8, 0.04)
    halo = ring([420, 630], 0.7, 0.04, 0.02)
    return polish(layer(warp, sweep, np.pad(halo, (int(0.32 * SR), 0))), drive=1.08, room_mix=0.26, echo_mix=0.05, air=0.05)


def points_increase_d() -> np.ndarray:
    out = np.zeros(int(SR * 1.9))
    freqs = [784, 932, 1175, 1047, 1397, 1760, 1568]
    t = 0.0
    for i, f in enumerate(freqs):
        chime = ring([f, f * 1.5, f * 2], 0.11, 0.05, 0.02)
        clip = layer(chime, stutter(chime * 0.42, 3, 0.7, 0.012))
        out = place(out, clip, t)
        t += 0.13 - min(i, 5) * 0.01
    return polish(out, drive=1.03, room_mix=0.12, echo_mix=0.03, air=0.05)


def victory_d() -> np.ndarray:
    intro = stutter(ring([659.25, 987.77], 0.24, 0.07, 0.03), 3, 0.72, 0.02)
    bloom = ring([523.25, 783.99, 1175.0], 1.05, 0.1, 0.03)
    tail = fm_tone(330, 7, 3.8, 0.42, 0.05) * env(int(SR * 0.42), 0.03, 0.16, 0.08, 0.2)
    return polish(layer(intro, np.pad(bloom, (int(0.12 * SR), 0)), np.pad(tail, (int(0.68 * SR), 0))), drive=1.04, room_mix=0.24, echo_mix=0.05, air=0.05)


def unsuccessful_d() -> np.ndarray:
    blip = stutter(chirp(480, 210, 0.26, 0.1) * env(int(SR * 0.26), 0.001, 0.12, 0.06, 0.18), 3, 0.68, 0.018)
    thunk = impact(132, 0.12, 0.09, 182, 0.06, ((1.0, 1.0), (1.5, 0.12)))
    return polish(layer(blip, np.pad(thunk, (int(0.24 * SR), 0))), drive=1.02, room_mix=0.12, echo_mix=0.02, air=0.03)


def ticking_clock_d() -> np.ndarray:
    out = np.zeros(int(SR * 3.2))
    spacing = [0.38, 0.28, 0.24, 0.18, 0.14, 0.1, 0.08]
    t = 0.0
    for i, s in enumerate(spacing):
        tick = highpass(noise(0.018, 0.11, 183 + i), 220) * env(int(SR * 0.018), 0.001, 0.02, 0.03, 0.06)
        tick = layer(tick, tone(1900 + i * 80, 0.022, 0.03) * env(int(SR * 0.022), 0.001, 0.02, 0.03, 0.05))
        out = place(out, stutter(tick, 2, 0.62, 0.012), t)
        t += s
    bed = fm_tone(88, 9, 5.5, 1.5, 0.04) * env(int(SR * 1.5), 0.06, 0.22, 0.08, 0.18)
    return polish(place(out, bed, 1.35), drive=1.03, room_mix=0.16, echo_mix=0.03, air=0.04)


def bonus_powerup_d() -> np.ndarray:
    lift = stutter(chirp(620, 1820, 0.22, 0.11) * env(int(SR * 0.22), 0.001, 0.08, 0.08, 0.14), 3, 0.76, 0.015)
    bloom = ring([880, 1175, 1760, 2349], 0.96, 0.07, 0.03)
    fizz = highpass(noise(0.22, 0.06, 190), 240) * env(int(SR * 0.22), 0.001, 0.08, 0.04, 0.16)
    return polish(layer(lift, np.pad(bloom, (int(0.16 * SR), 0)), np.pad(fizz, (int(0.08 * SR), 0))), drive=1.03, room_mix=0.24, echo_mix=0.05, air=0.05)


def render_catalog() -> dict[str, np.ndarray]:
    return {
        "01_rubber_stretch_a.wav": rubber_stretch_a(),
        "01_rubber_stretch_b.wav": rubber_stretch_b(),
        "01_rubber_stretch_c.wav": rubber_stretch_c(),
        "01_rubber_stretch_d.wav": rubber_stretch_d(),
        "02_projectile_release_a.wav": projectile_release_a(),
        "02_projectile_release_b.wav": projectile_release_b(),
        "02_projectile_release_c.wav": projectile_release_c(),
        "02_projectile_release_d.wav": projectile_release_d(),
        "03_blocks_falling_a.wav": blocks_falling_a(),
        "03_blocks_falling_b.wav": blocks_falling_b(),
        "03_blocks_falling_c.wav": blocks_falling_c(),
        "03_blocks_falling_d.wav": blocks_falling_d(),
        "04_core_hit_a.wav": core_hit_a(),
        "04_core_hit_b.wav": core_hit_b(),
        "04_core_hit_c.wav": core_hit_c(),
        "04_core_hit_d.wav": core_hit_d(),
        "05_small_explosion_a.wav": small_explosion_a(),
        "05_small_explosion_b.wav": small_explosion_b(),
        "05_small_explosion_c.wav": small_explosion_c(),
        "05_small_explosion_d.wav": small_explosion_d(),
        "06_big_explosion_a.wav": big_explosion_a(),
        "06_big_explosion_b.wav": big_explosion_b(),
        "06_big_explosion_c.wav": big_explosion_c(),
        "06_big_explosion_d.wav": big_explosion_d(),
        "07_background_music_loop_a.wav": background_music_a(),
        "07_background_music_loop_b.wav": background_music_b(),
        "07_background_music_loop_c.wav": background_music_c(),
        "07_background_music_loop_d.wav": background_music_d(),
        "08_ui_button_click_a.wav": ui_click_a(),
        "08_ui_button_click_b.wav": ui_click_b(),
        "08_ui_button_click_c.wav": ui_click_c(),
        "08_ui_button_click_d.wav": ui_click_d(),
        "09_slow_motion_zoom_a.wav": slow_motion_zoom_a(),
        "09_slow_motion_zoom_b.wav": slow_motion_zoom_b(),
        "09_slow_motion_zoom_c.wav": slow_motion_zoom_c(),
        "09_slow_motion_zoom_d.wav": slow_motion_zoom_d(),
        "10_points_increase_a.wav": points_increase_a(),
        "10_points_increase_b.wav": points_increase_b(),
        "10_points_increase_c.wav": points_increase_c(),
        "10_points_increase_d.wav": points_increase_d(),
        "11_victory_sound_a.wav": victory_a(),
        "11_victory_sound_b.wav": victory_b(),
        "11_victory_sound_c.wav": victory_c(),
        "11_victory_sound_d.wav": victory_d(),
        "12_unsuccessful_sound_a.wav": unsuccessful_a(),
        "12_unsuccessful_sound_b.wav": unsuccessful_b(),
        "12_unsuccessful_sound_c.wav": unsuccessful_c(),
        "12_unsuccessful_sound_d.wav": unsuccessful_d(),
        "13_clock_running_out_a.wav": ticking_clock_a(),
        "13_clock_running_out_b.wav": ticking_clock_b(),
        "13_clock_running_out_c.wav": ticking_clock_c(),
        "13_clock_running_out_d.wav": ticking_clock_d(),
        "14_bonus_powerup_a.wav": bonus_powerup_a(),
        "14_bonus_powerup_b.wav": bonus_powerup_b(),
        "14_bonus_powerup_c.wav": bonus_powerup_c(),
        "14_bonus_powerup_d.wav": bonus_powerup_d(),
    }


def main() -> None:
    os.makedirs(ASSET_DIR, exist_ok=True)
    for name, clip in render_catalog().items():
        save(name, clip)
        print(f"wrote {name}")


if __name__ == "__main__":
    main()
