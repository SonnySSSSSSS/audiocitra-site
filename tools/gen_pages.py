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


SOON_BANNER = '''<div class="wrap"><div class="soon-banner" role="note"><b>Coming soon</b><p>I&#39;m launching with Spanda and Ākāśa first so I can test them properly. {name} is next.. have a look around, it&#39;s all real, it just isn&#39;t out yet.</p></div></div>'''
SOON = {'galana', 'agni', 'shunya', 'lahari'}


def cta(name):
    return (f'<section><div class="wrap cta"><h2>Want to try {name}?</h2>'
            '<p class="soon">Trial&#39;s coming soon.. I&#39;m almost there</p><p class="lede req">VST3 · Windows 64-bit · licence, trial and signed updates right inside the plugin</p></div></section>')


def page(fn, title, desc, acc, eyebrow, h1, lede, hero_src, hero_alt, hero_cap, feat_head, fs, closeups, sk, cls=''):
    name = title.split()[0]
    key = fn.split('.')[0]
    n = len(TD[key]['layers'])
    grid = ('<div class="grid2">' + ''.join(plate(s, a) for s, a in closeups) + '</div>') if closeups else ''
    soon = SOON_BANNER.format(name=name) if key in SOON else ''
    out = HEAD.format(title=title, desc=e(desc), ogimg=hero_src, icon=ICON, acc=acc, cls=cls) + soon + f'''<div class="wrap">
  <header class="hero hero-tight"><span class="eyebrow">{eyebrow}</span><h1>{h1}</h1><p>{lede}</p>
  <div class="row"><a class="btn solid" href="#inside">Take it apart</a><a class="btn" href="#listen">Have a listen</a><a class="btn" href="#measurements">The plots</a></div></header>
  {plate(hero_src, hero_alt, False)}<p class="cap">{hero_cap}</p>
</div>
<div class="td" id="inside" data-teardown="{key}" style="--n:{n}"></div>
<section id="features"><div class="wrap"><div class="head"><span class="eyebrow">What's in here</span><h2>{feat_head}</h2></div>
  {grid}
  {feats(fs)}
</div></section>
<section id="listen"><div class="wrap"><div class="head"><span class="eyebrow">Listen</span><h2>Ok, have a listen.</h2>
  <p class="lede">Hit play and flip between Dry and {name}. I matched the loudness on both, so you're hearing what it actually does.. not just "louder sounds better".</p></div>
  <div class="listen" data-listen="{key}" data-name="{name}"></div>
</div></section>
<section id="measurements"><div class="wrap"><div class="head"><span class="eyebrow">Measurements</span><h2>I'd rather show you than tell you.</h2>
  <p class="lede">I ran every one of these offline through the plugin itself at 48 kHz. The settings I used are under each plot, so you can check my work.</p></div>
  <div class="meas-grid" data-meas="{key}"></div>
</div></section>
<section id="skins"><div class="wrap"><div class="head"><span class="eyebrow">Skins</span><h2>Pick a finish.</h2>
  <p class="lede">These are straight from the plugin, no mockups. Click around.. I spent way too long on some of these.</p></div>
  {sk}
</div></section>
{cta(name)}
''' + TAIL
    open(fn, 'w', encoding='utf-8').write(out)


page('galana.html', 'Gālana Effects Box',
     'Gālana is a VST3 effects box for Windows: twelve filter types, a Movement LFO, chorus and delay, run in any of six orders.',
     'galana', 'Gālana · effects box', 'Synth filters, <em>let off the leash.</em>',
     'So this one\'s my playground. Twelve filters I designed myself, a Movement section, chorus and delay.. and you can run those three stages in any of six orders. It\'s for when a sound just sits there and you need it to move.',
     'img/galana-hero.jpg', 'Gālana Field Radio skin rendered in 3D', 'Field Radio skin · 3D render',
     'Ok, here\'s <em>what\'s inside.</em>',
     [('Twelve filter types', 'Drive, Bite, Comb +, Comb −, Formant, Twin, Wave, Fold, Square, Crush, Ladder and Cascade. Drive, Bite, Twin and Wave each get eight modes: LP, HP and BP at 12 and 24 dB, plus Notch and All-pass. Nerd note: Bite gets its 24 dB modes by stacking two state-variable stages, which is a big part of why it bites.', '12 types · 8 modes'),
      ('Movement', 'An envelope, an LFO and a follower, all pushing the cutoff around. The LFO goes from a 1/16 note up to 2 bars, or free from 0.02 to 20 Hz, in seven shapes.. Steps, Glide and S&amp;H are my favourites. There\'s a step LFO too, with 4, 8 or 16 steps you draw yourself and a Glide to smooth them out. The envelope and the follower have their own attack, decay or release, and Movement can follow the input or a sidechain.', 'Envelope · LFO · follower'),
      ('Comb ±', 'One knob slides you from a feedforward comb into a feedback comb. I put a soft ceiling inside the feedback loop so it can ring like crazy without blowing up on you.', 'FF → FB · soft ceiling'),
      ('Chorus and delay', 'Four chorus styles: Classic, Wide, Slow and Fast. The delay works in note lengths, with feedback, tone and ping-pong.', '4 chorus styles · ping-pong'),
      ('Drive and saturation', 'Drive goes from -12 to +24 dB into one of nine saturation curves: Clean, Warm, Hard, Fold, Thick and four flavours of Asym. Hit Glue to pull it together, link Drive and Output if you want to push without getting louder, or let Auto Gain handle it.', '9 curves · Glue · Auto Gain'),
      ('Presets, A/B and undo', 'Presets with Previous/Next and folders, an A/B compare with a Copy button, and real undo/redo (Ctrl+Z) one move at a time. Presets only hold the sound, never your skin or size. Click the lotus for size (60–200%) and a separate oversampling setting just for offline bounces.', 'Presets · A/B · undo · render oversampling'),
      ('Six stage orders', 'Filter, Chorus and Delay can go in any of the six possible orders.. just pick one from the list. Delay into filter is a whole different animal than filter into delay, trust me. Filter oversampling goes Off, 2x, 4x or 8x.', '6 orders · oversampling')],
     [('img/galana-knobs.jpg', 'Cutoff, Resonance, Drive and Output chicken-head knobs'),
      ('img/galana-crt.jpg', 'The CRT showing the Comb + response')],
     skins(['Console', 'Field Radio'], ['Obsidian', 'Aether', 'HUD', 'Brutalist'], 'galana'))

page('agni.html', 'Agni Distortion',
     'Agni is a VST3 distortion for Windows: two engines that share ten shapes, five routings, a capture slot and cab impulse responses.',
     'agni', 'Agni · distortion', 'Two engines. <em>Ten shapes.</em>',
     'Two distortion engines, and each one picks from the same ten shapes. Then five ways to wire them, a feedback loop, a capture slot and cab IRs. Engine A can also turn into one of eight pedals.. I basically wanted my whole dirt rack in one box.',
     'img/agni-hero.jpg', 'Agni Valve rack skin rendered in 3D', 'Valve skin · rendered from the skin&#39;s own 3D plate',
     'Everything between <em>clean and totally gone.</em>',
     [('Pedal models', 'Flip Engine A from Custom to a pedal: Clean Boost, Tight Boost, Overdrive, Fuzz, Filter Distortion, Distortion, Metal or Octave Fuzz. Each one gets the three knobs you expect, Drive, Tone and Level, from 0 to 10. I fitted them to measurements and community captures of real pedals, clean blend and tone circuits included. Octave Fuzz even has its own octave-up stage. Switch back to Custom and your own engine settings come right back.', '8 pedals · Drive · Tone · Level'),
      ('Two engines, ten shapes', 'Each engine grabs its own shape from the same ten: Soft, Hard, Diode, Fold, Rectify, Tube, Transistor, Germanium, Tape and Crush. Turn Drive and Bias and the scope draws the transfer curve live.. honestly I could watch that thing all day.', '2 engines · 10 shapes'),
      ('Routings, feedback and modulation', 'Five ways to wire the two engines together, and a feedback loop wrapped around both. Two modulators (LFO or envelope) can push drive, tone, bias or balance around while you play.', '5 routings · feedback · 2 mods'),
      ('Capture and cab', 'Drop a neural capture (.nam) in after the engines, with a gate and a tight, mid or bright voicing in front of it. Then blend two cab IRs to taste. Oh, and Render Quality lets offline bounces run at a higher oversampling than you play at.', 'Capture slot · cab A/B')],
     [('img/agni-engine.jpg', 'Engine A: shape selector and Drive knob'),
      ('img/agni-master.jpg', 'Master section with twin VU meters')],
     skins(['Valve'], ['Forge', 'Slate', 'Citra', 'Pyre'], 'agni'))

page('akasa.html', 'Ākāśa Reverb',
     'Ākāśa is a VST3 reverb for Windows: six units fitted to the measured decay and colour of classic digital reverbs, with optional vintage converters.',
     'akasa', 'Ākāśa · coloured reverb', 'The rooms <em>you remember.</em>',
     'I measured how classic digital reverbs decay and colour the sound, and fitted these to that. Six units, three slots you can chain, wet EQ, presets and A/B. If you grew up on those old racks.. you\'ll hear it.',
     'img/akasa-b-detail.jpg', 'Oxblood skin close-up: reverb time knob and type display', 'Oxblood skin · close-up · 3D render',
     'Fitted to <em>what I measured.</em>',
     [('Megha', 'Halls, rooms, chambers and sheets, 22 programs, all true stereo. Flip on Motion and the tail starts to drift.', '22 programs · true stereo · Motion'),
      ('Guha', '14 programs.. halls, rooms and sheets, plus the fun ones: backward, echo and hold.', '14 programs'),
      ('Vayu', 'A synth-style reverb, with pre-delay, a colour filter and feedback routed back into the reverb. Weird in the best way.', 'Colour filter · feedback'),
      ('Dvaya', '77 two-effect presets that pair the reverb with delay, modulation, phaser or pitch blocks.', '77 presets'),
      ('Valuka and Adi', 'Simple little reverbs from the early digital days. Valuka has 100 programs (flanges and choruses in there too), Adi has 64. Lo-fi and charming.', '100 + 64 programs'),
      ('Optional converters', 'Set Converters to Vintage and you get the word length, word noise, idle floor and DC of old converters.. the grit nobody asked for but everybody misses. It\'s on Megha (on by default), Valuka and Adi (off by default).', 'Converters: Off · Vintage'),
      ('Three slots', 'Early, Mid and Late each hold any unit, and each feeds the next. Every slot gets pre-delay, width, cuts, shimmer and freeze. After those: a four-band wet EQ, ducking, chorus and a fidelity control, plus presets and A/B.', 'Early · Mid · Late · A/B'),
      ('FIT: Classic or Measured', 'This one is pure nerd stuff. I went back and refitted the late reverb of the clean units against my measurements with gradient descent. The FIT switch in the lotus panel lets you flip between Classic (the original fit) and Measured (the new one), with a crossfade, so you can judge for yourself.', 'FIT: Classic · Measured'),
      ('Auto Gain', 'On by default: the output sits at the same loudness as the input, so you\'re never fooled by a louder reverb.', 'Auto Gain')],
     [],
     skins(['Walnut', 'Orb', 'Oxblood'], ['Watercolor'], 'akasa'))

page('shunya.html', 'Shunya Reverb',
     'Shunya is a VST3 reverb for Windows: six clean reverb units with no saturation, drive or converter grain of their own.',
     'shunya', 'Shunya · transparent reverb', 'Clear space, <em>no grain added.</em>',
     'Ākāśa\'s quiet sibling. Shunya adds no saturation, drive or converter grain of its own.. just the space. Six units fitted to how classic reverbs measured, three slots you can chain, wet EQ, presets and A/B.',
     'img/shunya-hero.jpg', 'Shunya Graticule skin rendered in 3D, Mandapa on the display', 'Graticule skin &middot; Mandapa on the tube &middot; 3D render',
     'Six spaces, <em>one clean path.</em>',
     [('Mandapa', 'Hall, plate, room, chamber, ambience and space programs, true stereo, with a Motion control for the tail.', 'True stereo · Motion'),
      ('Vistara', 'Six algorithms: Hall, Random Hall, Plate, Ambience, Rich Plate and Concert Hall. You get size, pre-delay and diffusion to play with.', '6 algorithms'),
      ('Taranga', '11 reverb types, from halls and rooms all the way to a sheet, a tube and.. yep, a cellar. Plus 8 chorus types.', '11 reverbs · 8 choruses'),
      ('Dhvani', 'Eight types of room, stage, hall and echo, with delay feedback and three chorus types. And the chorus can feed into the reverb.', 'Chorus → reverb'),
      ('Kosha', 'Chambers, halls, a sheet and echoes, eight chorus types, and a send that pushes the chorus into the reverb.', 'Chorus → reverb'),
      ('Chatur', 'Rooms, sheets and shaped programs, plus Backward Swell and Gate Burst. 10 programs in all.', '10 programs'),
      ('Three slots', 'Early, Mid and Late each hold any unit and feed the next, so you can chain a room into a hall.. which I do constantly. After them: a four-band wet EQ, presets and A/B.', 'Early · Mid · Late · A/B'),
      ('FIT: Classic or Measured', 'Same nerd switch as Ākāśa. I refitted the late reverb against my measurements with gradient descent, and the FIT switch in the lotus panel flips between Classic and Measured with a crossfade. Mandapa also got new edge depths and a refit of its top-end damping.', 'FIT: Classic · Measured'),
      ('Auto Gain', 'On by default, so the output sits at the input\'s loudness.', 'Auto Gain')],
     [('img/shunya-crt.jpg', 'The phosphor tube showing Mandapa and its decay trace'),
      ('img/shunya-knobs.jpg', 'Mix knob close-up')],
     skins(['Graticule', 'Eclipse'], ['Washi', 'Blueprint'], 'shunya'), cls=' class="pale"')

def page_lite(fn, title, desc, acc, eyebrow, h1, lede, hero_src, hero_alt, hero_cap, feat_head, fs, sk, extra=''):
    # A product page without teardown, audio or measurements yet (a new plugin): hero, features, skins, call to action.
    name = title.split()[0]
    soon = SOON_BANNER.format(name=name) if fn.split('.')[0] in SOON else ''
    out = HEAD.format(title=title, desc=e(desc), ogimg=hero_src, icon=ICON, acc=acc, cls='') + soon + f'''<div class="wrap">
  <header class="hero hero-tight"><span class="eyebrow">{eyebrow}</span><h1>{h1}</h1><p>{lede}</p>
  <div class="row"><a class="btn solid" href="#features">What's in here</a><a class="btn" href="#skins">Skins</a></div></header>
  {plate(hero_src, hero_alt, False)}<p class="cap">{hero_cap}</p>
</div>
<section id="features"><div class="wrap"><div class="head"><span class="eyebrow">What's in here</span><h2>{feat_head}</h2></div>
  {feats(fs)}
  {extra}
</div></section>
<section id="skins"><div class="wrap"><div class="head"><span class="eyebrow">Skins</span><h2>Pick a finish.</h2>
  <p class="lede">These are straight from the plugin, no mockups. Click around.. I spent way too long on some of these.</p></div>
  {sk}
</div></section>
{cta(name)}
''' + TAIL
    open(fn, 'w', encoding='utf-8').write(out)


page_lite('lahari.html', 'Lahari Modulation',
     'Lahari is a VST3 modulation plugin for Windows: chorus, ensemble, celeste, flanger and phaser in six units.',
     'lahari', 'Lahari · modulation', 'Chorus, flanger, phaser. <em>Movement, in waves.</em>',
     'Six modulation units in one plugin: two choruses, an ensemble, a celeste, a flanger and a phaser. I fitted the choruses, ensemble, celeste and flanger to the chorus sections of classic digital units.. the phaser is my own thing. Every program plays exactly as fitted until you touch a knob.',
     'img/lahari-hero-analog.jpg', 'Lahari in the Analog skin, rendered in 3D', 'Analog skin &middot; 3D render',
     'Six units, <em>one set of hands.</em>',
     [('Nadi', 'A chorus with three programs: Stream, Ripple and Shiver.', 'Chorus · 3 programs'),
      ('Sarita', 'A big wide ensemble chorus, three programs, Ensemble I to III.', 'Chorus · 3 programs'),
      ('Yugala', 'A celeste.. that slow, detuned shimmer. Three programs, Shimmer I to III.', 'Celeste · 3 programs'),
      ('Bhramara', 'A flanger with two programs, Sweep I and II. Crank Feedback and it starts to ring all metallic.', 'Flanger · 2 programs'),
      ('Vrinda', 'The newest one: a big ensemble with seven programs, Octet, Drift, Echo, Throng, Weave, Spread and Choir. Lots of modulated taps, an optional amplitude swing and a crossed feedback echo. It gets thick fast.', 'Ensemble · 7 programs'),
      ('Chakra', 'My own phaser. Chains of 4 to 12 allpass stages, swept on a log scale, in four programs from Wheel to Whirl.', 'Phaser · 4 programs'),
      ('Shared controls', 'Rate and Depth scale the program\'s own values, Delay shifts its base delay or sweep range, and Feedback adds to its loop. Then Tone, Width, Mix and Output. Oversampling goes Off, 2x or 4x.', 'Rate ×0.25–×4 · Depth 0–200%'),
      ('Presets and size', '16 factory presets to start from: 6 chorus, 3 celeste, 3 flanger and 4 phaser. Click the logo for presets, skin, size (75–200%, or Ctrl +/−) and oversampling.', '16 presets · 75–200%')],
     skins([], ['Analog', 'Clean', 'Fantasy', 'Creative', 'Pedal'], 'lahari'),
     extra=plate('img/lahari-hero-pedal.jpg', 'Lahari in the Pedal skin, rendered in 3D') + '<p class="cap">Pedal skin &middot; 3D render</p>')

cards = [
    ('spanda.html', 'spanda', 'Channel strip', 'Spanda', 'Seven modules in one strip. Lots of it fitted to measurements, and parts you can mix and match.', 'img/con-cin-hero.jpg'),
    ('galana.html', 'galana', 'Effects box', 'Gālana', 'Twelve filters, a Movement section, chorus and delay, in any of six orders. Presets, A/B and undo.', 'img/galana-hero.jpg'),
    ('agni.html', 'agni', 'Distortion', 'Agni', 'Two engines, ten shapes, eight pedal models, five routings, a capture slot and cab IRs.', 'img/agni-hero.jpg'),
    ('akasa.html', 'akasa', 'Coloured reverb', 'Ākāśa', 'Six reverbs fitted to the decay and colour of classic digital units.. vintage converters optional.', 'img/akasa-b-detail.jpg'),
    ('shunya.html', 'shunya', 'Transparent reverb', 'Shunya', 'Six clean reverbs. No saturation, no drive, no grain. Just space.', 'img/shunya-hero.jpg'),
    ('lahari.html', 'lahari', 'Modulation', 'Lahari', 'Chorus, ensemble, celeste, flanger and phaser, six units, fitted to classic digital chorus sections.', 'img/lahari-hero-analog.jpg'),
]


def card(h, c, t, n, p, src):
    w, hh = Image.open(src).size
    th = f'<div class="thumb"><img src="{src}" alt="" width="{w}" height="{hh}" loading="lazy"></div>'
    badge = '<span class="soon-tag">Coming soon</span>' if c in SOON else ''
    return f'<a class="bay" href="{h}" style="--c:var(--{c})">{th}<span class="tag">{t}</span>{badge}<h3>{n}</h3><p>{p}</p></a>'


home = HEAD.format(title='Audio Citra', desc=e('Audio Citra makes six VST3 plugins for Windows: Spanda, Gālana, Agni, Ākāśa, Shunya and Lahari.'),
                   ogimg='img/lim-cin-hero.jpg', icon=ICON, acc='spanda', cls='') + f'''<div class="wrap">
  <header class="hero hero-tight"><span class="eyebrow">Hey, welcome in</span>
  <h1>I build plugins, <em>and this is where I keep them.</em></h1>
  <p>Pull up a chair. This is my little museum.. a channel strip, an effects box, a distortion, two reverbs and a modulation box. A lot of what they do is fitted to stuff I measured myself, and I built every one of them to feel good under your hands. All VST3, all Windows.</p>
  <div class="row"><a class="btn solid" href="spanda.html">start with Spanda</a><a class="btn" href="#plugins">see them all</a></div></header>
  {plate('img/lim-cin-hero.jpg', 'Spanda Limiter in the Cinematic skin, rendered in 3D', False)}
  <p class="cap">Spanda Limiter · Cinematic skin</p>
  <h2 class="sr">The plugins</h2>
  <div class="bays" id="plugins" style="padding-top:64px">{''.join(card(*c) for c in cards)}</div>
  <p class="proof">One thing I care about: every plot here I measured offline from the actual plugin, with the settings printed right next to it. And every audio clip is level-matched, dry vs processed. No tricks.. you hear what it does.</p>
</div>
''' + TAIL
open('index.html', 'w', encoding='utf-8').write(home)
print('ok')
