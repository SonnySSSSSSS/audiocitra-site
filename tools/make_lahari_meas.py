"""Lahari analysis plots for the site (img/meas/lahari_*.png) and their meas.json entries.
Rendered through the installed plug-in (E:/VST3/Lahari.vst3) at 48 kHz, program 0 of each unit, other controls at default.
    python tools/make_lahari_meas.py
"""
import os, json
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.signal import stft
from pedalboard import load_plugin

SR = 48000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "img", "meas")
UNITS = [("Nadi  Chorus", "Nadi · Stream"), ("Sarita  Chorus", "Sarita · Ensemble I"), ("Vrinda  Ensemble", "Vrinda · Octet"),
         ("Yugala  Celeste", "Yugala · Shimmer I"), ("Bhramara  Flanger", "Bhramara · Sweep I"), ("Chakra  Phaser", "Chakra · Wheel")]
COL = ["#5fd4b4", "#7fc8ff", "#c58bff", "#e895a0", "#ffb35c", "#ff6a3d"]
BG, FG, MUTE, GRID = "#0c0b10", "#ece9f2", "#8d8899", "#2a2733"
plt.rcParams.update({"font.family": "monospace", "text.color": FG, "axes.labelcolor": FG, "xtick.color": MUTE, "ytick.color": MUTE,
                     "axes.edgecolor": GRID, "axes.facecolor": BG, "figure.facecolor": BG, "font.size": 11})

p = load_plugin("E:/VST3/Lahari.vst3/Contents/x86_64-win/Lahari.vst3")
defaults = {k: v.raw_value for k, v in p.parameters.items()}
def run(x, unit, **kw):
    for k, v in defaults.items():
        try: p.parameters[k].raw_value = v
        except Exception: pass
    p.unit = unit; p.program = 0
    for k, v in kw.items(): setattr(p, k, v)
    return p.process(x.astype(np.float32), SR, reset=True)

def fig(title, sub):
    f = plt.figure(figsize=(12, 6.75), dpi=100)
    f.text(0.07, 0.93, title, fontsize=19); f.text(0.07, 0.885, sub, fontsize=10, color=MUTE)
    return f

# 1. a 1 kHz sine through each unit: how the pitch moves and spreads over 6 s
t = np.arange(int(7 * SR)) / SR
sine = np.tile(0.25 * np.sin(2 * np.pi * 1000 * t), (2, 1))
f = fig("Lahari · six units, six movements", "program 0 of each unit, mix 100 %, other controls at default · 1 kHz sine at -12 dBFS, left channel · 16k-point STFT, 75 % overlap")
for i, (u, name) in enumerate(UNITS):
    y = run(sine, u, mix=100)[0, SR:]
    fr, tt, Z = stft(y, SR, nperseg=16384, noverlap=12288)
    band = (fr > 920) & (fr < 1080)
    m = 20 * np.log10(np.abs(Z[band]) + 1e-9); m -= m.max()
    ax = f.add_axes([0.07 + (i % 3) * 0.31, 0.53 - (i // 3) * 0.42, 0.27, 0.3])
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list("c", [BG, COL[i]])
    ax.pcolormesh(tt, fr[band], m, vmin=-50, vmax=0, cmap=cmap, shading="auto")
    ax.set_title(name, loc="left", fontsize=12, color=FG); ax.set_ylim(920, 1080)
    ax.set_yticks([950, 1000, 1050]); ax.set_xlabel("Time (s)" if i >= 3 else "")
    if i % 3 == 0: ax.set_ylabel("Hz")
f.savefig(os.path.join(OUT, "lahari_units_pitch.png")); plt.close(f)

# 2. white noise through the flanger and the phaser: the notches sweeping
rng = np.random.default_rng(1); noise = rng.standard_normal((2, 9 * SR)) * 0.1
f = fig("Lahari · flanger and phaser, sweeping", "white noise at -20 dBFS RMS, mix 50 %, left channel · Bhramara Sweep I with feedback +40, Chakra Wheel at default · 4k-point STFT")
for i, (u, name, kw, c) in enumerate([("Bhramara  Flanger", "Bhramara · Sweep I, feedback +40", {"feedback": 40}, COL[4]), ("Chakra  Phaser", "Chakra · Wheel", {}, COL[5])]):
    y = run(noise, u, mix=50, **kw)[0, SR:]
    fr, tt, Z = stft(y, SR, nperseg=4096, noverlap=3072)
    keep = (fr >= 50) & (fr <= 16000)
    m = 20 * np.log10(np.abs(Z[keep]) + 1e-9)
    from scipy.ndimage import uniform_filter
    m = uniform_filter(m, (3, 3)); m -= np.percentile(m, 99)
    ax = f.add_axes([0.07 + i * 0.47, 0.12, 0.42, 0.68])
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list("c", [BG, c, "#fff3dc"])
    ax.pcolormesh(tt, fr[keep], m, vmin=-30, vmax=0, cmap=cmap, shading="auto")
    ax.set_yscale("log"); ax.set_ylim(50, 16000); ax.set_yticks([100, 300, 1000, 3000, 10000]); ax.set_yticklabels(["100", "300", "1k", "3k", "10k"])
    ax.set_title(name, loc="left", fontsize=12, color=FG); ax.set_xlabel("Time (s)")
    if i == 0: ax.set_ylabel("Frequency (Hz)")
f.savefig(os.path.join(OUT, "lahari_sweeps.png")); plt.close(f)

# 3. stereo: a mono source comes out wide, and the mono sum keeps its level
f = fig("Lahari · width, and what's left in mono", "pink-ish noise, mono in, mix 100 %, program 0 of each unit · level of L+R and L-R relative to the dry mono input, 1/3-octave")
pink = np.cumsum(rng.standard_normal(10 * SR)); pink -= np.convolve(pink, np.ones(4800) / 4800, "same"); pink = 0.1 * pink / pink.std()
x = np.tile(pink, (2, 1))
ax = f.add_axes([0.08, 0.12, 0.86, 0.68])
def third(sig):
    S = np.abs(np.fft.rfft(sig * np.hanning(len(sig)))) ** 2; fr = np.fft.rfftfreq(len(sig), 1 / SR)
    cs = 1000 * 2 ** (np.arange(-17, 14) / 3)
    return cs, np.array([10 * np.log10(S[(fr >= c / 2 ** (1 / 6)) & (fr < c * 2 ** (1 / 6))].mean() + 1e-20) for c in cs])
cs, ref = third(pink[SR:])
for i, (u, name) in enumerate(UNITS):
    y = run(x, u, mix=100)[:, SR:]
    _, mid = third((y[0] + y[1]) / 2); _, side = third((y[0] - y[1]) / 2)
    ax.semilogx(cs, mid - ref, color=COL[i], lw=1.8, label=name + " · mono sum")
    ax.semilogx(cs, side - ref, color=COL[i], lw=1.2, ls="--", alpha=.8)
ax.set_xlim(40, 16000); ax.set_ylim(-36, 6); ax.grid(color=GRID, lw=.6, which="both")
ax.set_xticks([50, 100, 200, 500, 1000, 2000, 5000, 10000]); ax.set_xticklabels(["50", "100", "200", "500", "1k", "2k", "5k", "10k"])
ax.set_xlabel("Frequency (Hz)"); ax.set_ylabel("Level re dry (dB)")
ax.legend(loc="lower left", fontsize=9, ncol=2, frameon=False); ax.text(15000, 3, "solid: L+R  ·  dashed: L-R (the width)", ha="right", color=MUTE, fontsize=10)
f.savefig(os.path.join(OUT, "lahari_width_mono.png")); plt.close(f)
print("plots written")
