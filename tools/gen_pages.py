"""Generates galana/agni/akasa/shunya.html and index.html. spanda.html is hand-written (keep it in sync by hand).
Run: python gen_pages.py <website dir>. Reads teardown.json (layer counts) and the image files (pixel sizes)."""
import os, sys, json, html
from PIL import Image

os.chdir(sys.argv[1])
TD = json.load(open('teardown.json', encoding='utf-8'))

ICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E"
        "%3Crect width='32' height='32' rx='7' fill='%230c0b10'/%3E"
        "%3Ccircle cx='16' cy='16' r='7' fill='none' stroke='%23c58bff' stroke-width='3'/%3E%3C/svg%3E")

HEAD = '''<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:type" content="website"><meta property="og:site_name" content="Audio Citra">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{ogimg}">
<link rel="icon" href="{icon}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Syne:wght@500;700;800&family=Instrument+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="site.css">
<style>body{{--accent:var(--{acc})}}</style>
</head><body{cls}>
<main id="main">
'''
TAIL = '''</main>
<script src="site.js"></script>
</body></html>
'''


def e(s):
    return html.escape(s, quote=True)


def img(src, alt, lazy=True):
    w, h = Image.open(src).size
    lz = ' loading="lazy"' if lazy else ''
    return f'<img src="{src}" alt="{e(alt)}" width="{w}" height="{h}"{lz}>'


def plate(src, alt, lazy=True):
    return f'<figure class="plate" style="margin:0">{img(src, alt, lazy)}</figure>'


def feats(fs):
    return '<div class="feats">' + ''.join(
        f'<div class="feat"><h3>{h}</h3><p>{p}</p><span class="spec">{s}</span></div>' for h, p, s in fs) + '</div>'


def skins(d3, flat, key=None):
    # With key: a working switcher over img/skins/{key}-{skin}.jpg, first skin shown.
    if not key:
        return ('<div class="skins">' + ''.join(f'<span class="d3">{s} · 3D</span>' for s in d3)
                + ''.join(f'<span>{s} · flat</span>' for s in flat) + '</div>')
    from PIL import Image
    all_ = [(s, '3D') for s in d3] + [(s, 'flat') for s in flat]
    src = lambda s: f'img/skins/{key}-{s.lower().replace(" ", "-")}.jpg'
    w, h = Image.open(src(all_[0][0])).size
    btns = ''.join(f'<button aria-pressed="{"true" if i == 0 else "false"}" data-src="{src(s)}">{s}</button>'
                   for i, (s, _) in enumerate(all_))
    label = {'galana': 'Gālana', 'akasa': 'Ākāśa'}.get(key, key.capitalize())
    return (f'<figure class="plate" style="margin:0"><img id="i-skin" src="{src(all_[0][0])}" '
            f'alt="{label} editor, {all_[0][0]} skin" width="{w}" height="{h}" loading="lazy"></figure>'
            f'<div class="seg" data-swap="i-skin" aria-label="Skin" style="margin-top:12px">{btns}</div>')


def cta(name):
    return (f'<section><div class="wrap cta"><h2>Want to try {name}?</h2>'
            '<p class="soon">Trial coming soon</p><p class="lede req">VST3 · Windows 64-bit</p></div></section>')


def page(fn, title, desc, acc, eyebrow, h1, lede, hero_src, hero_alt, hero_cap, feat_head, fs, closeups, sk, cls=''):
    name = title.split()[0]
    key = fn.split('.')[0]
    n = len(TD[key]['layers'])
    grid = ('<div class="grid2">' + ''.join(plate(s, a) for s, a in closeups) + '</div>') if closeups else ''
    out = HEAD.format(title=title, desc=e(desc), ogimg=hero_src, icon=ICON, acc=acc, cls=cls) + f'''<div class="wrap">
  <header class="hero hero-tight"><span class="eyebrow">{eyebrow}</span><h1>{h1}</h1><p>{lede}</p>
  <div class="row"><a class="btn solid" href="#inside">Take it apart</a><a class="btn" href="#listen">Listen</a><a class="btn" href="#measurements">Measurements</a></div></header>
  {plate(hero_src, hero_alt, False)}<p class="cap">{hero_cap}</p>
</div>
<div class="td" id="inside" data-teardown="{key}" style="--n:{n}"></div>
<section id="features"><div class="wrap"><div class="head"><span class="eyebrow">What it does</span><h2>{feat_head}</h2></div>
  {grid}
  {feats(fs)}
</div></section>
<section id="listen"><div class="wrap"><div class="head"><span class="eyebrow">Listen</span><h2>Hear it, dry and through {name}.</h2>
  <p class="lede">Press play, then switch between Dry and {name}. Both are matched in loudness, so you hear the change, not the volume.</p></div>
  <div class="listen" data-listen="{key}" data-name="{name}"></div>
</div></section>
<section id="measurements"><div class="wrap"><div class="head"><span class="eyebrow">Measurements</span><h2>Measured, not described.</h2>
  <p class="lede">Each plot is measured offline from the plugin at 48 kHz. Settings are listed under each one.</p></div>
  <div class="meas-grid" data-meas="{key}"></div>
</div></section>
<section id="skins"><div class="wrap"><div class="head"><span class="eyebrow">Skins</span><h2>Pick a finish.</h2>
  <p class="lede">Every skin, captured from the plugin itself. Pick one to see it.</p></div>
  {sk}
</div></section>
{cta(name)}
''' + TAIL
    open(fn, 'w', encoding='utf-8').write(out)


page('galana.html', 'Gālana Effects Box',
     'Gālana is a VST3 effects box for Windows: twelve filter types, a Movement LFO, chorus and delay, run in any of six orders.',
     'galana', 'Gālana · effects box', 'Synth filters, <em>set loose.</em>',
     'Twelve filters of our own design, a Movement section, chorus and delay. Run the three stages in any of six orders. For when a sound needs to move.',
     'img/galana-hero.jpg', 'Gālana Field Radio skin rendered in 3D', 'Field Radio skin · 3D render',
     'Filters with <em>room to move.</em>',
     [('Twelve filter types', 'Drive, Bite, Comb +, Comb −, Formant, Twin, Wave, Fold, Square, Crush, Ladder and Cascade. Drive, Bite, Twin and Wave offer eight modes: LP, HP and BP at 12 and 24 dB, Notch and All-pass. Bite builds its 24 dB modes from two stacked state-variable stages.', '12 types · 8 modes'),
      ('Movement', 'An envelope, an LFO and a follower move the cutoff. The LFO runs from a 1/16 note to 2 bars, or free from 0.02 to 20 Hz, in seven shapes including Steps, Glide and S&amp;H. Movement can follow the input or a sidechain.', 'Envelope · LFO · follower'),
      ('Comb ±', 'Crossfade from a feedforward to a feedback comb, with a soft ceiling in the feedback loop.', 'FF → FB · soft ceiling'),
      ('Chorus and delay', 'Chorus has four styles: Classic, Wide, Slow and Fast. The delay is set in note lengths, with feedback, tone and ping-pong.', '4 chorus styles · ping-pong'),
      ('Six stage orders', 'Filter, Chorus and Delay can run in any of six orders, picked from a list. Oversampling on the filter can be Off, 2x, 4x or 8x.', '6 orders · oversampling')],
     [('img/galana-knobs.jpg', 'Cutoff, Resonance, Drive and Output chicken-head knobs'),
      ('img/galana-crt.jpg', 'The CRT showing the Comb + response')],
     skins(['Console', 'Field Radio'], ['Obsidian', 'Aether', 'HUD', 'Brutalist'], 'galana'))

page('agni.html', 'Agni Distortion',
     'Agni is a VST3 distortion for Windows: two engines that share ten shapes, five routings, a capture slot and cab impulse responses.',
     'agni', 'Agni · distortion', 'Two engines. <em>Ten shapes.</em>',
     'Two distortion engines that each pick from the same ten shapes, with five routings, a feedback loop, a capture slot and cab IRs, all in one box.',
     'img/agni-hero.jpg', 'Agni Valve rack skin rendered in 3D', 'Valve skin · rendered from the skin&#39;s own 3D plate',
     'Everything between <em>clean and gone.</em>',
     [('Two engines, ten shapes', 'Each engine picks its own shape from the same ten: Soft, Hard, Diode, Fold, Rectify, Tube, Transistor, Germanium, Tape and Crush. Set Drive and Bias; the scope shows the transfer curve as you turn them.', '2 engines · 10 shapes'),
      ('Routings, feedback and modulation', 'Five ways to wire the two engines, with a feedback loop around the pair. Two modulators (LFO or envelope) can move drive, tone, bias or balance.', '5 routings · feedback · 2 mods'),
      ('Capture and cab', 'Load a neural capture (.nam) after the engines, with a gate and a tight, mid and bright voicing in front of it. Then blend two cab impulse responses.', 'Capture slot · cab A/B')],
     [('img/agni-engine.jpg', 'Engine A: shape selector and Drive knob'),
      ('img/agni-master.jpg', 'Master section with twin VU meters')],
     skins(['Valve'], ['Forge', 'Slate', 'Citra', 'Pyre'], 'agni'))

page('akasa.html', 'Ākāśa Reverb',
     'Ākāśa is a VST3 reverb for Windows: six units fitted to the measured decay and colour of classic digital reverbs, with optional vintage converters.',
     'akasa', 'Ākāśa · coloured reverb', 'The rooms <em>you remember.</em>',
     'Reverbs fitted to the measured decay and colour of classic digital units. Six units, three slots you can chain, wet EQ, presets and A/B.',
     'img/akasa-b-detail.jpg', 'Oxblood skin close-up: reverb time knob and type display', 'Oxblood skin · close-up · 3D render',
     'Fitted to <em>what was measured.</em>',
     [('Megha', 'Hall, room, chamber and sheet programs, 22 in all, in true stereo. Motion turns on tail modulation.', '22 programs · true stereo · Motion'),
      ('Guha', '14 programs, including halls, rooms, sheets, and backward, echo and hold effects.', '14 programs'),
      ('Vayu', 'A synth-style reverb with pre-delay, a colour filter and feedback routings into the reverb.', 'Colour filter · feedback'),
      ('Dvaya', '77 two-effect presets that combine reverb with delay, modulation, phaser and pitch blocks.', '77 presets'),
      ('Valuka and Adi', 'Simple reverbs of the early digital era. Valuka has 100 programs, including flanges and choruses; Adi has 64.', '100 + 64 programs'),
      ('Optional converters', 'Set Converters to Vintage to add the word length, word noise, idle floor and DC of vintage converters. It is on Megha (on by default), Valuka and Adi (off by default).', 'Converters: Off · Vintage'),
      ('Three slots', 'Early, Mid and Late each hold any unit and feed the next. Each slot has pre-delay, width, cuts, shimmer and freeze. After them: a four-band wet EQ, ducking, chorus and a fidelity control, with presets and A/B.', 'Early · Mid · Late · A/B')],
     [],
     skins(['Walnut', 'Orb', 'Oxblood'], ['Watercolor'], 'akasa'))

page('shunya.html', 'Shunya Reverb',
     'Shunya is a VST3 reverb for Windows: six clean reverb units with no saturation, drive or converter grain of their own.',
     'shunya', 'Shunya · transparent reverb', 'Clear space, <em>no grain added.</em>',
     'Shunya adds no saturation, drive or converter grain of its own. Six units fitted to the measured behaviour of classic reverbs, three slots you can chain, wet EQ, presets and A/B.',
     'img/shunya-hero.jpg', 'Shunya Graticule skin rendered in 3D, Mandapa on the display', 'Graticule skin &middot; Mandapa on the tube &middot; 3D render',
     'Six spaces, <em>one clean path.</em>',
     [('Mandapa', 'Hall, plate, room, chamber, ambience and space programs in true stereo, with a Motion control for the tail.', 'True stereo · Motion'),
      ('Vistara', 'Six algorithms: Hall, Random Hall, Plate, Ambience, Rich Plate and Concert Hall, with size, pre-delay and diffusion controls.', '6 algorithms'),
      ('Taranga', '11 reverb types, from halls and rooms to a sheet, a tube and a cellar, plus 8 chorus types.', '11 reverbs · 8 choruses'),
      ('Dhvani', 'Eight types of room, stage, hall and echo, with delay feedback and three chorus types. The chorus can feed the reverb.', 'Chorus → reverb'),
      ('Kosha', 'Chambers, halls, a sheet and echoes, with eight chorus types and a send that feeds the chorus into the reverb.', 'Chorus → reverb'),
      ('Chatur', 'Rooms, sheets and shaped programs, plus Backward Swell and Gate Burst: 10 programs in all.', '10 programs'),
      ('Three slots', 'Early, Mid and Late each hold any unit and feed the next, so you can chain a room into a hall. After them: a four-band wet EQ, presets and A/B.', 'Early · Mid · Late · A/B')],
     [('img/shunya-crt.jpg', 'The phosphor tube showing Mandapa and its decay trace'),
      ('img/shunya-knobs.jpg', 'Mix knob close-up')],
     skins(['Graticule', 'Eclipse'], ['Washi', 'Blueprint'], 'shunya'), cls=' class="pale"')

def page_lite(fn, title, desc, acc, eyebrow, h1, lede, hero_src, hero_alt, hero_cap, feat_head, fs, sk, extra=''):
    # A product page without teardown, audio or measurements yet (a new plugin): hero, features, skins, call to action.
    name = title.split()[0]
    out = HEAD.format(title=title, desc=e(desc), ogimg=hero_src, icon=ICON, acc=acc, cls='') + f'''<div class="wrap">
  <header class="hero hero-tight"><span class="eyebrow">{eyebrow}</span><h1>{h1}</h1><p>{lede}</p>
  <div class="row"><a class="btn solid" href="#features">What it does</a><a class="btn" href="#skins">Skins</a></div></header>
  {plate(hero_src, hero_alt, False)}<p class="cap">{hero_cap}</p>
</div>
<section id="features"><div class="wrap"><div class="head"><span class="eyebrow">What it does</span><h2>{feat_head}</h2></div>
  {feats(fs)}
  {extra}
</div></section>
<section id="skins"><div class="wrap"><div class="head"><span class="eyebrow">Skins</span><h2>Pick a finish.</h2>
  <p class="lede">Every skin, captured from the plugin itself. Pick one to see it.</p></div>
  {sk}
</div></section>
{cta(name)}
''' + TAIL
    open(fn, 'w', encoding='utf-8').write(out)


page_lite('lahari.html', 'Lahari Modulation',
     'Lahari is a VST3 modulation plugin for Windows: chorus, celeste, flanger and phaser in five units.',
     'lahari', 'Lahari · modulation', 'Chorus, flanger, phaser. <em>Movement, in waves.</em>',
     'Five modulation units in one plugin: two choruses, a celeste, a flanger and a phaser. The choruses, celeste and flanger are fitted to the chorus sections of classic digital units; the phaser is our own design. Every program plays as fitted until you move a knob.',
     'img/lahari-hero-analog.jpg', 'Lahari in the Analog skin, rendered in 3D', 'Analog skin &middot; 3D render',
     'Five units, <em>one set of hands.</em>',
     [('Nadi', 'A chorus with three programs: Stream, Ripple and Shiver.', 'Chorus · 3 programs'),
      ('Sarita', 'A wide ensemble chorus with three programs, Ensemble I to III.', 'Chorus · 3 programs'),
      ('Yugala', 'A celeste: a slow, detuned shimmer with three programs, Shimmer I to III.', 'Celeste · 3 programs'),
      ('Bhramara', 'A flanger with two programs, Sweep I and II. Feedback pushes it towards a metallic ring.', 'Flanger · 2 programs'),
      ('Chakra', 'Our own phaser: chains of 4 to 12 allpass stages swept on a log scale, in four programs from Wheel to Whirl.', 'Phaser · 4 programs'),
      ('Shared controls', 'Rate and Depth scale the program\'s own values, Delay moves its base delay or sweep range, and Feedback adds to its loop. Then Tone, Width, Mix and Output.', 'Rate ×0.25–×4 · Depth 0–200%')],
     skins([], ['Analog', 'Clean', 'Fantasy', 'Creative', 'Pedal'], 'lahari'),
     extra=plate('img/lahari-hero-pedal.jpg', 'Lahari in the Pedal skin, rendered in 3D') + '<p class="cap">Pedal skin &middot; 3D render</p>')

cards = [
    ('spanda.html', 'spanda', 'Channel strip', 'Spanda', 'Seven modules in one strip, with many behaviours fitted to measurements and parts you can combine.', 'img/con-cin-hero.jpg'),
    ('galana.html', 'galana', 'Effects box', 'Gālana', 'Twelve filter types, a Movement LFO, chorus and delay, run in any of six orders.', 'img/galana-hero.jpg'),
    ('agni.html', 'agni', 'Distortion', 'Agni', 'Two engines that share ten shapes, five routings, a capture slot and cab IRs.', 'img/agni-hero.jpg'),
    ('akasa.html', 'akasa', 'Coloured reverb', 'Ākāśa', 'Six reverb units fitted to the decay and colour of classic digital reverbs, with optional vintage converters.', 'img/akasa-b-detail.jpg'),
    ('shunya.html', 'shunya', 'Transparent reverb', 'Shunya', 'Six clean reverb units with no saturation, drive or converter grain of their own.', 'img/shunya-hero.jpg'),
    ('lahari.html', 'lahari', 'Modulation', 'Lahari', 'Chorus, celeste, flanger and phaser in five units, fitted to classic digital chorus sections.', 'img/lahari-hero-analog.jpg'),
]


def card(h, c, t, n, p, src):
    w, hh = Image.open(src).size
    th = f'<div class="thumb"><img src="{src}" alt="" width="{w}" height="{hh}" loading="lazy"></div>'
    return f'<a class="bay" href="{h}" style="--c:var(--{c})">{th}<span class="tag">{t}</span><h3>{n}</h3><p>{p}</p></a>'


home = HEAD.format(title='Audio Citra', desc=e('Audio Citra makes six VST3 plugins for Windows: Spanda, Gālana, Agni, Ākāśa, Shunya and Lahari.'),
                   ogimg='img/lim-cin-hero.jpg', icon=ICON, acc='spanda', cls='') + f'''<div class="wrap">
  <header class="hero hero-tight"><span class="eyebrow">Six instruments for mixing, tone and space</span>
  <h1>Tools for tone and space, <em>played like instruments.</em></h1>
  <p>A channel strip, an effects box, a distortion, two reverbs and a modulation box. Many of their behaviours are fitted to measurements, and each is built to respond to your hands. VST3 for Windows.</p>
  <div class="row"><a class="btn solid" href="spanda.html">Meet Spanda</a><a class="btn" href="#plugins">All plugins</a></div></header>
  {plate('img/lim-cin-hero.jpg', 'Spanda Limiter in the Cinematic skin, rendered in 3D', False)}
  <p class="cap">Spanda Limiter · Cinematic skin</p>
  <h2 class="sr">The plugins</h2>
  <div class="bays" id="plugins" style="padding-top:64px">{''.join(card(*c) for c in cards)}</div>
  <p class="proof">Why Audio Citra: every plot on this site is measured offline from the plugin with its settings printed beside it, and every audio clip is level-matched, dry against processed.</p>
</div>
''' + TAIL
open('index.html', 'w', encoding='utf-8').write(home)
print('ok')
