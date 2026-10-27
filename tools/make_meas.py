"""Copy the measurement plots into the site and write website/meas.json (captions + settings per plugin)."""
import json, os, shutil
M = r'D:\AI\TAM\.claude\worktrees\website-showcase\marketing\shots\measurements'
W = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # site root
SEL = {
 'spanda': [
  ('spanda_eq_curves', 'EQ: four bands, measured', 'The shelves and bells land where the knobs say.', 'Low shelf 100 Hz, bells 500 Hz and 3 kHz, high shelf 8 kHz · each band alone at ±6 and ±12 dB · −18 dBFS sweep'),
  ('spanda_eq_q_family', 'EQ: bell width', 'From a broad tilt to a narrow peak, all from one bell band.', '1 kHz bell, +9 dB, Q 0.3 to 6'),
  ('spanda_dynamics_static_curve', 'Dynamics: static curve', 'Measured input against output for four ratios.', 'Threshold −24 dB, knee 6 dB, ratios 2, 4, 10 and 20 · stepped 1 kHz sine'),
  ('spanda_dynamics_step_response', 'Dynamics: attack and release', 'Gain reduction over time for a level step.', '−40 → −6 → −40 dBFS step · threshold −24 dB, 4:1 · three attack/release pairs'),
  ('spanda_finisher_logos_harmonics', 'Finisher: Logos harmonics', 'A 1 kHz tone picks up harmonics as you push the drive.', 'Logos, bias 6, drive 3 vs 12 · 1 kHz at −12 dBFS'),
  ('spanda_limiter_true_peak', 'Limiter: true-peak ceiling', 'Push it 18 dB past full scale and the output still stops at −1 dBTP.', 'Transparent mode, ceiling −1.0 dBTP · noise bursts and a 997 Hz sine, −12 to +18 dBFS · 4x-oversampled meter'),
 ],
 'galana': [
  ('galana_filter_lp24_cutoff', 'LP 24 across the range', 'A 24 dB/oct low-pass from 100 Hz to 10 kHz.', 'Drive type, resonance 0, Clean, drive 0 · −30 dBFS sweep'),
  ('galana_filter_lp24_resonance', 'Resonance', 'The peak rises past +15 dB and the bass thins as it does.', 'LP 24 at 1 kHz, resonance 0 to 115'),
  ('galana_filter_hp24_cutoff', 'HP 24 across the range', 'A 24 dB/oct high-pass at full level.', 'Drive type, resonance 0 · −30 dBFS sweep'),
  ('galana_filter_bp24_cutoff', 'BP 24 across the range', 'Band-pass from 100 Hz to 10 kHz.', 'Drive type, resonance 0 · −30 dBFS sweep'),
  ('galana_filter_types_compared', 'Three filter cores', 'Same knob settings, three different shapes.', 'Drive, Ladder and Cascade · LP 24, 1 kHz, resonance 96'),
  ('galana_comb_plus', 'Comb +', 'Tuned resonant teeth across the whole spectrum.', '500 Hz, resonance 32 / 80 / 115'),
 ],
 'agni': [
  ('agni_transfer_curves', 'Ten shapes, ten curves', 'Each shape bends the signal its own way. The loops come from the slot\u2019s filters adding phase shift.', 'Slot A, drive +12 dB, bias 0 · one cycle of a 0 dBFS 100 Hz sine · quality 4x'),
  ('agni_harmonic_spectra', 'Harmonics', 'Odd harmonics from the symmetric shapes, even and odd from Tube and Germanium.', 'Drive +12 dB · 1 kHz at −6 dBFS'),
  ('agni_aliasing_1x_vs_8x', 'Oversampling', 'The worst alias falls from −24 dBFS at 1x to −82 dBFS at 8x.', 'Hard shape, drive +24 dB · 7 kHz tone at −6 dBFS'),
 ],
 'akasa': [
  ('akasa_rt60_per_octave', 'Six units, six decays', 'Reverb time per octave for every unit, measured.', 'Default programs · T20 per octave'),
  ('akasa_wet_response_per_unit', 'Each unit\u2019s colour', 'The wet spectrum of all six units.', 'Default programs · 1/3-octave smoothed'),
  ('akasa_megha_decay_per_octave', 'Megha: decay per octave', 'The highs die away faster than the lows, as in a real hall. With the default Vintage converters, quiet tails end at the 16-bit floor, as the original does.', 'Grand Hall, defaults · −6 dBFS impulse'),
 ],
 'shunya': [
  ('shunya_rt60_per_octave', 'Reverb time per octave', 'Every unit\u2019s decay across the spectrum.', 'Default programs · T20 per octave'),
  ('shunya_wet_response_per_unit', 'Wet response per unit', 'No tone stage of its own: what you see is each space\u2019s air, its highs fading like a real room.', 'Default programs · 1/3-octave smoothed'),
  ('shunya_kosha_decay_per_octave', 'Kosha: decay per octave', 'A smooth, even decay in every band.', 'Hall B, defaults'),
 ],
}
out = {}
for plug, items in SEL.items():
    d = os.path.join(W, 'img', 'meas'); os.makedirs(d, exist_ok=True)
    out[plug] = []
    for name, title, cap, settings in items:
        shutil.copy2(os.path.join(M, plug, name + '.png'), os.path.join(d, name + '.png'))
        out[plug].append({'src': 'img/meas/%s.png' % name, 'title': title, 'caption': cap, 'settings': settings})
# Tulā's plots come from AudioCitraFree/tools/meas/tula_meas.py and are already in img/meas: keep them
out['tula'] = json.load(open(os.path.join(W, 'meas.json'), encoding='utf-8')).get('tula', [])
json.dump(out, open(os.path.join(W, 'meas.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('ok', sum(len(v) for v in out.values()))
