"""The drum loop every hero capture plays (the panels only need to move, nobody hears it): 2 bars at 120 bpm = 4.000 s, 48 kHz
stereo 24-bit, peaking at -1 dBFS so a limiter or compressor at its defaults works on every hit. 4 s at 25 fps = 100 frames,
so a capture of one pass (after a pass of preroll) loops without a seam.
  python hero_loop.py <out.wav>"""
import sys, wave, numpy as np
SR, BPM, BARS = 48000, 120, 2
n = int(SR * 60 / BPM * 4 * BARS); t = np.arange(n) / SR; x = np.zeros((n, 2))
rng = np.random.default_rng(7); beat = 60 / BPM
def hit(at, sig, pan=0.0):
    i = int(at * SR); s = sig[: n - i]; x[i:i + len(s), 0] += s * (1 - pan); x[i:i + len(s), 1] += s * (1 + pan)
tt = np.arange(int(0.5 * SR)) / SR
kick = np.sin(2 * np.pi * (50 * tt + 60 / 25 * (1 - np.exp(-25 * tt)))) * np.exp(-tt * 9)
snare = (rng.standard_normal(len(tt)) * 0.6 * np.exp(-tt * 22) + np.sin(2 * np.pi * 190 * tt) * 0.5 * np.exp(-tt * 30))
hat = rng.standard_normal(len(tt)) * np.exp(-tt * 90); hat = np.diff(hat, prepend=0) * 0.5
for b in range(4 * BARS):
    hit(b * beat, kick if b % 2 == 0 else snare)
    if b % 4 == 3: hit(b * beat + beat / 2, kick * 0.7)
    for k in range(2): hit(b * beat + k * beat / 2, hat * (0.5 if k else 0.35), pan=0.3)
x *= 10 ** (-1 / 20) / np.abs(x).max()
pcm = (np.clip(x, -1, 1) * (2 ** 23 - 1)).astype('<i4')
raw = b"".join(int(v).to_bytes(4, "little", signed=True)[:3] for v in pcm.reshape(-1))
with wave.open(sys.argv[1], "wb") as w: w.setnchannels(2); w.setsampwidth(3); w.setframerate(SR); w.writeframes(raw)
print("wrote", sys.argv[1], n / SR, "s")
