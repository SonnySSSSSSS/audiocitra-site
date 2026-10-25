"""Spanda PARTS data for the site: website/parts.json + img/parts/*.jpg.
Text is transcribed from origin/main src/Spanda/Source/Plugin/PartsCatalog.h (compressorCatalogSpec, eqCatalogSpec)
and the choice lists in PluginProcessor.cpp. Card art: src/Spanda/Resources/parts_collectibles."""
import json, os, sys
from PIL import Image

SRC = os.path.join(os.environ['TEMP'], 'pc')          # extracted parts_collectibles
W = sys.argv[1]                                        # website dir
os.makedirs(os.path.join(W, 'img', 'parts'), exist_ok=True)


def lesson(s):
    use, _, bg = s.partition(' | ')
    return use.split(': ', 1)[-1], bg.replace('Background: ', '')


def slot(sid, stem, name, guide, options, notes, lessons):
    opts = []
    for i, o in enumerate(options):
        img = None
        if stem:
            src = os.path.join(SRC, '%s_%d.jpg' % (stem, i))
            img = 'img/parts/%s_%d.jpg' % (stem, i)
            im = Image.open(src).convert('RGB')
            im.resize((800, round(800 * im.height / im.width)), Image.LANCZOS).save(os.path.join(W, img), quality=80, optimize=True)
        use, bg = lesson(lessons[i]) if lessons else ('', '')
        opts.append({'name': o, 'img': img, 'note': notes[i], 'use': use, 'bg': bg})
    return {'id': sid, 'name': name, 'guide': guide, 'options': opts}


comp = [
    slot('sense', 'comp_sense', 'Sense', 'What the detector listens to.',
         ['Peak', 'RMS', 'Opto', 'Feedback'],
         ['Follows every peak: fast and tight.', 'Follows the average level over about 10 ms: smoother.',
          'A slower average, about 40 ms, like an optical cell.',
          'Listens to its own compressed output: it can never fully catch up, so it eases in and sounds smoother. Ratio tops out at 5:1.'],
         ['Use on: drums, percussion, plucked bass: anything whose hits must be caught. | Background: peak sensing is how fast VCA and FET compressors catch transients.',
          'Use on: vocals, bass, full mixes; it follows loudness the way the ear does. | Background: RMS detection became the standard of VCA bus compressors from the late 1970s.',
          'Use on: vocals, bass guitar, strings: smooth, program-dependent levelling. | Background: optical cells (a lamp or LED lighting a photo-resistor) made 1960s levelling amplifiers famous.',
          'Use on: mix bus, acoustic instruments, gentle vocal levelling. | Background: most vintage tube and optical compressors are feedback designs; hearing their own output gives their relaxed feel.']),
    slot('curve', 'comp_curve', 'Curve', 'How the gain reduction grows above the threshold.',
         ['Hard', 'Soft', 'Ratio-linked knee', 'Rising', 'Drive into knee', 'Limit', 'Vari-mu'],
         ['No knee: the full ratio starts right at the threshold.', 'Eases in over the width set by the Knee control.',
          'The knee width follows the ratio, widest at middle ratios.', 'The ratio climbs as it compresses harder.',
          'A fixed 3.5:1 with a wide 11 dB knee.', 'A fixed 6.5:1 limiter curve with a 7 dB knee.',
          'A gentle 2.3:1 with a short 4 dB knee, like a variable-mu tube.'],
         ['Use on: drum bus, parallel smash, peak control: obvious and punchy. | Background: hard knees are typical of fast VCA and FET units.',
          "Use on: vocals and the mix bus, where the start of compression should not be heard. | Background: soft knees spread with the 'over-easy' VCA designs of the late 1970s.",
          'Use on: general duty when you move the ratio a lot; it stays natural at every setting.',
          'Use on: bass and vocals that swing between soft and loud: gentle on quiet parts, firm on loud ones. | Background: a ratio that rises with level is a trait of many tube and optical designs.',
          'Use on: vocals and guitars for a classic levelling sound. | Background: a moderate fixed ratio over a wide knee is the optical levelling-amplifier recipe.',
          'Use on: vocal peaks, room mics, loud drums: limiting with a soft edge. | Background: fixed high ratios with a knee are typical of broadcast limiters.',
          "Use on: mix bus and mastering glue: gentle, low-ratio compression. | Background: a variable-mu tube's gain falls smoothly as its bias changes, which keeps the ratio low."]),
    slot('grab', 'comp_grab', 'Grab', 'How it clamps down when the level jumps.',
         ['Single', 'Two-step', 'Instant', 'Knock', 'Vari-mu build'],
         ['One smooth attack at the Attack time.', 'Two attack stages in a row, for a softer start.',
          'Much faster: about a sixth of the Attack time.', "The Knock compressor's own grab and curve (Curve is set aside).",
          'A slow build over about 90 ms, whatever the Attack control says.'],
         ['Use on: anything; the standard attack.',
          'Use on: kick and snare when the click should pass but the body be held. | Background: a two-stage onset imitates the softer start of optical and tube gain cells.',
          "Use on: peak catching, aggressive drums, room mics. | Background: very fast attack is the FET compressor's signature.",
          'Use on: drums and bass that need bite and punch. | Background: analyzed from a classic FET compressor.',
          'Use on: mix bus and pads: transients pass, then it settles slowly. | Background: variable-mu tubes respond slowly by nature.']),
    slot('letgo', 'comp_letgo', 'Let go', 'How it recovers after the level drops.',
         ['Plain', 'Snap', 'Glide', 'Two-stage', 'Release B'],
         ['One smooth release at the Release time.', 'A fast release, 40 ms at most.', 'Recovers at a steady rate, then eases out.',
          'A fast 60 ms recovery, then a slow tail that builds only while it works hard.', 'Lets go faster the deeper it is compressing.'],
         ['Use on: anything; the standard release.',
          'Use on: drum rooms and aggressive parallel compression: pumping and loudness.',
          'Use on: vocals and bass for an even, predictable recovery. | Background: a steady recovery rate is how many optical and VCA circuits let go.',
          "Use on: the mix bus and full mixes: quick after transients, slow under sustained loudness. | Background: a dual-time-constant ('auto') release is the classic bus-compressor trick.",
          'Use on: dense material and vocals; it avoids long holes after big hits. | Background: program-dependent release is a hallmark of optical cells.']),
    slot('colour', 'comp_colour', 'Colour', 'Harmonic colour added by the compressor.',
         ['Clean', 'Triode', 'Pentode', 'Transformer', 'Tape', 'Dense', 'FET', 'Knock'],
         ['No colour.', 'Even-harmonic tube warmth.', 'Tube saturation that gets edgier as it is driven.',
          'Saturates the lows (below about 120 Hz) more.', 'Saturates the highs (above about 3 kHz) more.',
          'Thickens the peaks: gentle odd-harmonic density.', 'A touch of even harmonics, like a FET stage.',
          "The Knock compressor's own harmonics."],
         ['Use on: classical, acoustic and mastering work, where the dynamics should be invisible.',
          "Use on: vocals, bass, keys: warmth and fullness. | Background: triode stages produce mostly second harmonic, the 'tube warmth' of classic preamps.",
          'Use on: guitars, synths, drum bus: bite when pushed. | Background: pentode stages add more odd harmonics as they are driven.',
          "Use on: kick, bass, 808s: weight and thickness in the lows. | Background: audio transformers saturate first at low frequencies, where the core's flux is highest.",
          'Use on: drums, mix bus, acoustic guitar: softened, glued highs. | Background: hit hard, magnetic tape saturates and partly erases its own high frequencies.',
          'Use on: drums and loud rock: fatter peaks without obvious distortion.',
          'Use on: vocals and snare: subtle presence. | Background: FET gain stages add a little, mostly even, harmonic content.',
          'Use on: drums and bass. | Background: the analyzed harmonics of a classic FET compressor.']),
    slot('place', 'comp_place', 'Colour place', 'Where the colour sits in the chain.',
         ['After gain', 'Before detector'],
         ['Colours the compressed signal.', 'Colours the input, so the compressor reacts to the coloured sound.'],
         ['Use for: the classic outboard sound; the colour sits after the gain, as in most hardware.',
          "Use for: thicker, more interactive compression; the compressor reacts to the colour, like driving a unit's input stage."]),
    slot('driver', 'comp_driver', 'Colour driver', 'What makes the colour stronger.',
         ['Input', 'Gain reduction', 'Output level', 'Knee position'],
         ['Steady, set by Colour amount.', 'More colour the harder it compresses.', 'More colour on louder output.',
          'More colour as the signal passes through the knee.'],
         ['Use for: a constant flavour, whatever the music does.',
          'Use on: drums and the bus: the harder it works, the more it colours, like a tube compressor running out of headroom.',
          'Use on: loud sections: colour that blooms with the music.',
          'Use on: vocals: colour appears where compression starts, and quiet parts stay clean.']),
]

shelf = ['Plain', 'British', 'Passive', 'Class-A', 'American', 'Mastering']
shelf_notes = ['The shelf exactly as dialled.',
               'British console: a softer shelf that turns about an octave from the knob.',
               'Passive tube program EQ: a very gentle low shelf; the high boost is a broad bell.',
               'British class-A module: a firm shelf that turns well past the knob; cuts slope gently.',
               'American console module: a broad, smooth shelf; the low one reaches well past the knob.',
               'Passive tube mastering EQ: raise Q for a resonant shelf with a dip beside it.']
shelf_lessons = ['Use when: you want exactly what you dial, for surgical and mastering moves.',
                 'Use on: drums, vocals, modern pop and rock: punchy and a little hyped. | Background: the EQ of British large-format consoles from the late 1970s and 1980s.',
                 'Use on: kick, bass, vocals, the mix bus: huge gentle lows and a silky top. | Background: a 1950s passive tube program equalizer; boosting and cutting the same low band was its famous trick.',
                 'Use on: vocals, guitars, drums: thick, musical shelves. | Background: 1970s British class-A console modules with inductor EQ.',
                 'Use on: drums, guitars, bass: forward and punchy. | Background: American console modules known for their proportional-Q EQ.',
                 'Use on: mastering and the mix bus: big, smooth shelves; raise Q for the resonant bump. | Background: a modern passive tube mastering EQ with adjustable shelf bandwidth.']
bell = ['Plain', 'British', 'Class-A', 'American', 'Precision', 'Passive', 'Mastering']
bell_notes = ['The bell exactly as dialled.',
              'British console: much broader than its Q says, tighter as you boost.',
              'British class-A module: one broad fixed width, tighter as you boost. Q is not used.',
              'American console module: proportional Q, cuts mirror boosts. Q is not used.',
              'Mastering parametric: a clean bell whose width follows the Q you dial.',
              'Passive tube mid EQ: broad boosts low down, tighter up top; the cut is deeper and narrower. Q is not used.',
              'Passive tube mastering EQ: a very broad bell that narrows as you boost; Q sets how broad.']
bell_lessons = ['Use when: you want exactly what you dial, for surgical cuts and precise boosts.',
                'Use on: snare crack, vocal presence, guitar bite: broad and forgiving. | Background: British large-format console mids, wider than their Q markings suggest.',
                'Use on: vocals and guitars: broad, musical boosts that tighten as you push. | Background: 1970s British class-A console modules with a fixed-width mid.',
                'Use on: snare, toms, guitars: boosts that narrow as you push, so big moves stay focused. | Background: proportional-Q, the signature of American console EQ.',
                'Use on: mastering and the mix bus: narrow, exact moves that keep the width you set. | Background: a 1970s American mastering parametric equalizer, analyzed from a sampled copy (up to 6 dB).',
                'Use on: vocals, guitars, the mix bus: a gentle presence lift or a mud dip with tube-EQ manners. | Background: the 1950s passive tube mid-range equalizer that partnered the program EQ, analyzed from a sampled copy.',
                "Use on: mastering and the mix bus: wide, gentle tone moves that never sound like an EQ. | Background: a modern passive tube mastering EQ's mid band, analyzed on the unit."]
eq = [
    slot('low', 'eq_low', 'Low band', "How the low band's shelf turns.", shelf, shelf_notes, shelf_lessons),
    slot('lowmid', 'eq_lowmid', 'Low-mid band', 'How wide the low-mid bell is.', bell, bell_notes, bell_lessons),
    slot('highmid', 'eq_highmid', 'High-mid band', 'How wide the high-mid bell is.', bell, bell_notes, bell_lessons),
    slot('high', 'eq_high', 'High band', "How the high band's shelf turns.", shelf, shelf_notes, shelf_lessons),
]

out = {
    'comp': {'tab': 'Compressor', 'slots': comp,
             'note': 'Threshold, Ratio, Knee, Attack, Release and Makeup stay on the panel. If a part sets one of them, it locks it there.. that's the part doing its job.',
             'default': [1, 1, 0, 0, 0, 0, 0],
             # recipes from compressorRecipes() (sense, curve, grab, letGo, colour, place, driver)
             'recipes': [['Bus Glue', [1, 1, 0, 4, 0, 0, 0]], ['Opto Level', [2, 4, 1, 3, 1, 0, 1]],
                         ['Thick Bus', [1, 3, 0, 3, 3, 0, 0]], ['Knee Tube', [1, 1, 0, 3, 1, 0, 3]],
                         ['Knock-like', [0, 0, 2, 1, 6, 0, 1]]]},
    # eqRecipes(): low, lowMid, highMid, high
    'eq': {'tab': 'EQ', 'slots': eq,
           'note': 'Frequency, Gain, Q and the shelf switches stay on the panel. Each band takes its own part, so go wild.',
           'default': [0, 0, 0, 0],
           'recipes': [['Clean', [0, 0, 0, 0]], ['British class-A', [3, 2, 2, 3]], ['American', [4, 3, 3, 4]],
                       ['Passive ends, British mids', [2, 1, 1, 2]], ['Mastering shelves, American mids', [5, 3, 3, 5]]]},
}
json.dump(out, open(os.path.join(W, 'parts.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('ok', sum(len(s['options']) for s in comp), sum(len(s['options']) for s in eq))
