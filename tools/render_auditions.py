"""Render dry/processed audition pairs for the product website.

Usage:  python render_auditions.py            # all plugins, one subprocess per plugin
        python render_auditions.py --plugin Agni [--smoke]
        python render_auditions.py --finish-only

Each plugin renders in its own BelowNormal subprocess with a timeout (one plugin process at a time).
Pairs are loudness-matched (integrated LUFS, pyloudnorm), true peak capped at -1 dBTP, dry ~-16 LUFS.
"""
import os, sys, json, subprocess, argparse
import numpy as np, soundfile as sf
try:
    import psutil; psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
except Exception:
    pass

SR = 48000
HERE = os.path.dirname(os.path.abspath(__file__))
STEMS = r"D:\AI\Spanda_Audition_Stems"
TMP = os.path.join(HERE, "_tmp")
AUDIO = os.path.join(os.path.dirname(HERE), "audio")
TARGET = -16.0
TP_CAP = -1.0
CC_BY_DRUMS = ('"Chill Groove Multitrack Drums" by boxboy333 (ccmixter.org/files/boxboy333/41488), CC BY 3.0')

# id, title, stem, clip length s, tail s, settings, summary, credit
CLIPS = {
 "Spanda": [
  ("spanda-1", "Vocal · console + compressor + EQ", "Vocal - Female (dry).wav", 12, 0,
   dict(console_active=True, console_flavor="Signature",
        compressor=True, comp_voicing="VCA", comp_vca_voicing="Smooth", comp_threshold_db=-26.0, comp_ratio=3.0,
        comp_knee_db=6.0, comp_attack_ms=8.0, comp_release_ms=150.0, comp_auto_makeup=True,
        eq=True, eq_voicing="Digital", eq_hpf_mode="Precision", eq_hpf_frequency_hz=90.0,
        eq_low_mid_freq_hz=300.0, eq_low_mid_gain_db=-2.5, eq_high_mid_freq_hz=3000.0, eq_high_mid_gain_db=2.0,
        eq_high_freq_hz=10000.0, eq_high_gain_db=3.0),
   "Spanda EQ (90 Hz high-pass, -2.5 dB at 300 Hz, +2 dB at 3 kHz, +3 dB air shelf at 10 kHz), Dynamics (VCA Smooth, 3:1, -26 dB threshold, 8 ms / 150 ms, auto makeup) and Console (Signature)", None),
  ("spanda-2", "Drums · Dynamics + Limiter", "Drums - Electronic.wav", 12, 0,
   dict(compressor=True, comp_voicing="FET", fet_mode="Balanced", comp_threshold_db=-22.0, comp_ratio=4.0,
        comp_attack_ms=20.0, comp_release_ms=80.0, comp_auto_makeup=True,
        limiter=True, limiter_mode="Transient", limiter_threshold_db=-6.0, limiter_ceiling_dbtp=-1.0),
   "Dynamics (FET, Balanced, 4:1, -22 dB threshold, 20 ms attack, 80 ms release) into Limiter (Transient mode, 6 dB drive, -1 dBTP ceiling)", None),
  ("spanda-3", "Full mix · bus chain", "Full Mix.wav", 13, 0,
   dict(console_active=True, console_flavor="Signature", tape_active=True, tape_drive_db=2.0,
        compressor=True, comp_voicing="VCA", comp_vca_voicing="BUS SNAP", comp_threshold_db=-20.0, comp_ratio=2.0,
        comp_attack_ms=30.0, comp_release_ms=300.0, comp_auto_makeup=True,
        eq=True, eq_voicing="Digital", eq_low_freq_hz=80.0, eq_low_gain_db=1.5, eq_high_freq_hz=12000.0, eq_high_gain_db=1.5,
        limiter=True, limiter_mode="Smooth", limiter_threshold_db=-3.0, limiter_ceiling_dbtp=-1.0),
   "Bus chain: Console (Signature), Tape (+2 dB drive), Dynamics (VCA Bus Snap, 2:1, 30 ms / 300 ms), EQ (+1.5 dB low and high shelves), Limiter (Smooth, 3 dB, -1 dBTP)", None),
 ],
 "Galana": [
  ("galana-1", "Pad · moving filter", "Pad - Warm.wav", 12, 2,
   dict(filter_type="Drive", filter_mode="LP 24", cutoff=900.0, resonance=70.0, drive=3.0, env_amount=0.0,
        lfo_depth=36.0, lfo_rate="1 bar", lfo_shape="Sine", chorus_mix=30.0, delay_mix=15.0),
   "Drive filter, LP 24, 900 Hz cutoff, resonance 70, movement LFO (sine, 1 bar, depth 36), chorus 30 %, delay 15 %", None),
  ("galana-2", "Drums · Comb +", "Drums - Electronic.wav", 12, 0,
   dict(filter_type="Comb +", cutoff=420.0, resonance=85.0, drive=0.0, filter_mix=60.0, env_amount=20.0,
        chorus_on=False, delay_on=False),
   "Comb + filter at 420 Hz, resonance 85, envelope 20, filter mix 60 %, chorus and delay off", None),
  ("galana-3", "Bass · resonant ladder LP", "Bass - Saw.wav", 12, 0,
   dict(filter_type="Ladder", filter_mode="LP 24", cutoff=350.0, resonance=95.0, drive=6.0, env_amount=40.0,
        env_decay=220.0, lfo_depth=0.0, chorus_on=False, delay_on=False),
   "Ladder filter, LP 24, 350 Hz cutoff, resonance 95, +6 dB drive, envelope 40 with 220 ms decay, chorus and delay off", None),
 ],
 "Agni": [
  ("agni-1", "Bass · Tube", "Bass - Saw.wav", 12, 0,
   dict(a_on=True, a_shape="Tube", a_drive_db=18.0, a_post_lp_hz=9000.0, b_on=False, nam_on=False, cab_on=False, mix=100.0),
   "Stage A Tube shape, 18 dB drive, 9 kHz post low-pass, 100 % wet; capture and cab off", None),
  ("agni-2", "Drums · Germanium", "Drums - Electronic.wav", 12, 0,
   dict(a_on=True, a_shape="Germanium", a_drive_db=14.0, a_post_lp_hz=12000.0, b_on=False, nam_on=False, cab_on=False, mix=65.0),
   "Stage A Germanium shape, 14 dB drive, 12 kHz post low-pass, 65 % mix (parallel); capture and cab off", None),
  ("agni-3", "Synth lead · Rectify", "Lead - Synth.wav", 12, 0,
   dict(a_on=True, a_shape="Rectify", a_drive_db=10.0, a_post_lp_hz=10000.0, b_on=False, nam_on=False, cab_on=False, mix=60.0),
   "Stage A Rectify shape, 10 dB drive, 10 kHz post low-pass, 60 % mix; capture and cab off", None),
 ],
 "Akasa": [
  ("akasa-1", "Vocal · Megha hall", "Vocal - Song (a cappella).wav", 11, 2.5,
   dict(unit="Megha", megha_program="Clear Hall", pre_delay_ms=30.0, low_cut_hz=150.0, mix=25.0, input_db=0.0),
   "Megha unit, Clear Hall program, 30 ms pre-delay, 150 Hz low cut, 25 % mix", None),
  ("akasa-2", "Drums · Guha room", "Drums - Acoustic (Groove).wav", 11, 2,
   dict(unit="Guha", guha_program="Room One", mix=25.0, input_db=0.0),
   "Guha unit, Room One program, default decay, 25 % mix", CC_BY_DRUMS),
 ],
 "Shunya": [
  ("shunya-1", "Vocal · Mandapa", "Vocal - Female (dry).wav", 11, 2.5,
   dict(unit="Mandapa", pre_delay_ms=20.0, low_cut_hz=120.0, mix=25.0, input_db=0.0),
   "Mandapa unit, short hall (1.6 s), 20 ms pre-delay, 120 Hz low cut, 25 % mix", None),
  ("shunya-2", "Electric piano · Vistara plate", "Keys - Electric Piano.wav", 11, 2.5,
   dict(unit="Vistara", vistara_algorithm="Plate", mix=25.0, input_db=0.0),
   "Vistara unit, Plate algorithm, default time, 25 % mix", None),
 ],
}


def load_plugin_inner(name):
    from pedalboard import load_plugin
    return load_plugin(f"E:/VST3/{name}.vst3/Contents/x86_64-win/{name}.vst3")


def pick_window(x, secs):
    """Start (samples) of the loudest `secs` window on a 0.5 s grid."""
    n = int(secs * SR); hop = SR // 2
    m = (x ** 2).mean(axis=0)
    c = np.concatenate([[0], np.cumsum(m)])
    best, bs = -1, 0
    for s in range(0, max(1, len(m) - n), hop):
        e = c[s + n] - c[s]
        if e > best: best, bs = e, s
    return bs


def render_plugin(name, smoke):
    p = load_plugin_inner(name)
    noise = (np.random.default_rng(0).standard_normal((2, SR)) * 0.05).astype(np.float32)
    y = p.process(noise, SR, reset=True)
    assert np.all(np.isfinite(y)) and np.abs(y).max() > 1e-4, "smoke render failed"
    print(name, "smoke ok, peak", float(np.abs(y).max()), flush=True)
    if smoke: return
    os.makedirs(TMP, exist_ok=True)
    defaults = {k: v.raw_value for k, v in p.parameters.items()}
    for cid, title, stem, secs, tail, settings, summary, credit in CLIPS[name]:
        for k, v in defaults.items():
            try: p.parameters[k].raw_value = v
            except Exception: pass
        for k, v in settings.items():
            setattr(p, k, v)
        x, sr = sf.read(os.path.join(STEMS, stem), dtype="float32", always_2d=True)
        assert sr == SR
        x = x.T
        s = pick_window(x, secs); pre = min(2 * SR, s)
        n = int(secs * SR)
        seg = x[:, s - pre: s + n].copy()
        if tail:  # let the reverb ring: fade the music out, then silence
            f = int(0.3 * SR); seg[:, -f:] *= np.linspace(1, 0, f)
            seg = np.concatenate([seg, np.zeros((2, int(tail * SR)), np.float32)], axis=1)
        wet = p.process(seg, SR, reset=True)[:, pre:]
        dry = seg[:, pre:]
        assert np.all(np.isfinite(wet))
        sf.write(os.path.join(TMP, f"{cid}-dry.wav"), dry.T, SR, subtype="FLOAT")
        sf.write(os.path.join(TMP, f"{cid}-wet.wav"), wet.T, SR, subtype="FLOAT")
        print(cid, "rendered, start", round(s / SR, 1), "s, raw wet peak", float(np.abs(wet).max()), flush=True)


def true_peak_db(x):
    from scipy.signal import resample_poly
    up = resample_poly(x, 4, 1, axis=1)
    return 20 * np.log10(np.abs(up).max() + 1e-12)


def fade(x):
    a, b = int(0.02 * SR), int(0.3 * SR)
    x = x.copy(); x[:, :a] *= np.linspace(0, 1, a); x[:, -b:] *= np.linspace(1, 0, b)
    return x


def decode_mp3(path):
    dec = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path, "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(dec, np.float32).reshape(-1, 2).T.astype(np.float64)


def finish():
    import pyloudnorm as pyln
    meter = pyln.Meter(SR)
    out = []
    for name, clips in CLIPS.items():
        for cid, title, stem, secs, tail, settings, summary, credit in clips:
            d, _ = sf.read(os.path.join(TMP, f"{cid}-dry.wav"), always_2d=True); d = fade(d.T)
            w, _ = sf.read(os.path.join(TMP, f"{cid}-wet.wav"), always_2d=True); w = fade(w.T)
            ld, lw = meter.integrated_loudness(d.T), meter.integrated_loudness(w.T)
            target = TARGET
            for _ in range(3):  # lower both together until the louder-peaking one sits under the cap (MP3 margin)
                gd, gw = 10 ** ((target - ld) / 20), 10 ** ((target - lw) / 20)
                tp = max(true_peak_db(d * gd), true_peak_db(w * gw))
                if tp <= TP_CAP - 0.3: break
                target -= tp - (TP_CAP - 0.3)
            d, w = d * gd, w * gw
            stats = {}
            for tag, sig in (("dry", d), ("wet", w)):
                path = os.path.join(AUDIO, f"{cid}-{tag}.mp3")
                tmpw = os.path.join(TMP, f"{cid}-{tag}-final.wav")
                sf.write(tmpw, sig.T, SR, subtype="PCM_24")
                subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmpw, "-b:a", "192k", path], check=True)
                m = decode_mp3(path)
                stats[tag] = dict(lufs=round(meter.integrated_loudness(m.T), 2), tp=round(true_peak_db(m), 2),
                                  rms=round(10 * np.log10((m ** 2).mean() + 1e-20), 2),
                                  dur=round(m.shape[1] / SR, 2))
            out.append(dict(plugin=name, id=cid, title=title, source_stem=stem, settings_summary=summary,
                            dry=f"{cid}-dry.mp3", wet=f"{cid}-wet.mp3",
                            lufs_dry=stats["dry"]["lufs"], lufs_wet=stats["wet"]["lufs"], credit=credit))
            print(cid, "target", round(target, 2), stats, flush=True)
    with open(os.path.join(AUDIO, "clips.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--plugin"); ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--finish-only", action="store_true")
    a = ap.parse_args()
    if a.plugin:
        render_plugin(a.plugin, a.smoke); sys.exit(0)
    if not a.finish_only:
        for name in CLIPS:  # one plugin process at a time, each with a timeout
            for smoke, to in ((True, 120), (False, 600)):
                subprocess.run([sys.executable, __file__, "--plugin", name] + (["--smoke"] if smoke else []),
                               check=True, timeout=to)
    finish()
