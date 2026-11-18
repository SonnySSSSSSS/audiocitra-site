"""Spanda PARTS data for the site: parts.json + img/parts/*.jpg, read straight from the Spanda repo's origin/main so the
site lists every part the plug-in has. Run:  python tools/make_parts.py <website dir> [<spanda repo>]

Text comes from src/Spanda/Source/Plugin/PartsCatalog.h (setGuide / setLessons in compressorCatalogSpec and eqCatalogSpec,
recipes from compressorRecipes / eqRecipes), option names from Core/PartsWizardRecipes.h, the numbers in the guide text
from Core/PartsBasketCompressor.h, and the card art from src/Spanda/Resources/parts_collectibles."""
import io, json, os, re, subprocess, sys
from PIL import Image

W = sys.argv[1]
REPO = sys.argv[2] if len(sys.argv) > 2 else r'D:\AI\Spanda-engine'
REF = 'origin/main'
subprocess.run(['git', '-C', REPO, 'fetch', '-q', 'origin'], check=True)
HASH = subprocess.run(['git', '-C', REPO, 'rev-parse', '--short', REF], capture_output=True, text=True, check=True).stdout.strip()


def show(path, binary=False):
    out = subprocess.run(['git', '-C', REPO, 'show', f'{REF}:{path}'], check=True, capture_output=True).stdout
    return out if binary else out.decode('utf-8')


cat = show('src/Spanda/Source/Plugin/PartsCatalog.h')
pb = show('src/Spanda/Source/Core/PartsBasketCompressor.h')
wiz = show('src/Spanda/Source/Core/PartsWizardRecipes.h')
CONST = {m[0]: float(m[1]) for m in re.findall(r'inline constexpr double (k\w+) = ([\d.]+)', pb)}


def names(arr):
    m = re.search(r'std::array<const char\*, \d+> %s\{(.*?)\};' % arr, wiz)
    return re.findall(r'"([^"]*)"', m[1])


def body(fn):
    i = cat.index('inline %s()' % fn)
    j = cat.index('\n}\n', i)
    return cat[i:j]


def ratio(r):
    s = ('%.1f' % r).rstrip('0').rstrip('.')
    return s + ':1'


def cpp_string(expr):
    """One C++ string expression: literals, bt::ratio(...) and bt::db(...) joined by +."""
    out = ''
    for tok in re.finditer(r'"((?:[^"\\]|\\.)*)"|bt::(ratio|db)\(([^()]*)\)', expr):
        if tok[1] is not None:
            out += tok[1].replace('\\"', '"').replace("\\'", "'")
        else:
            v = eval(re.sub(r'pb::(k\w+)', lambda m: repr(CONST[m[1]]), tok[3]))
            out += ratio(v) if tok[2] == 'ratio' else '%d dB' % round(v)
    return out


def items(block):
    """Split a { a, b + c, ... } list at its top-level commas."""
    parts, depth, cur, q = [], 0, '', False
    for i, ch in enumerate(block):
        if ch == '"' and block[i - 1] != '\\':
            q = not q
        if not q:
            if ch in '({':
                depth += 1
            elif ch in ')}':
                depth -= 1
            elif ch == ',' and depth == 0:
                parts.append(cur); cur = ''; continue
        cur += ch
    if cur.strip():
        parts.append(cur)
    return [cpp_string(p) for p in parts]


def braced(src, start):
    i = src.index('{', start); depth = 0
    for j in range(i, len(src)):
        depth += src[j] == '{'
        depth -= src[j] == '}'
        if depth == 0:
            return src[i + 1:j], j


def guides(spec_src):
    """parameter id -> (about, notes, lessons); named lists (const juce::StringArray x{...}) are resolved."""
    named = {}
    for m in re.finditer(r'const juce::StringArray (\w+)\{', spec_src):
        named[m[1]] = items(braced(spec_src, m.end() - 1)[0])
    g = {}
    for m in re.finditer(r'set(Guide|Lessons)\(spec, "(\w+)",', spec_src):
        rest = spec_src[m.end():]
        if m[1] == 'Guide':
            # scan the about expression to its top-level ',' or ')', skipping over string literals and calls
            i, depth, q = 0, 0, False
            while True:
                ch = rest[i]
                if ch == '"' and rest[i - 1] != chr(92):
                    q = not q
                elif not q:
                    if ch == '(':
                        depth += 1
                    elif ch == ')' and depth:
                        depth -= 1
                    elif depth == 0 and ch in ',)':
                        break
                i += 1
            about = cpp_string(rest[:i])
            if rest[i] == ',':
                tail = rest[i + 1:].lstrip()
                notes = items(braced(tail, 0)[0]) if tail.startswith('{') else named[re.match(r'(\w+)', tail)[1]]
            else:
                notes = []
            g.setdefault(m[2], {}).update(about=about, notes=notes)
        else:
            tail = rest.lstrip()
            g.setdefault(m[2], {})['lessons'] = items(braced(tail, 0)[0]) if tail.startswith('{') else named[re.match(r'(\w+)', tail)[1]]
    return g


def lesson(s):
    use, _, bg = s.partition(' | ')
    return use.split(': ', 1)[-1], bg.replace('Background: ', '')


os.makedirs(os.path.join(W, 'img', 'parts'), exist_ok=True)


def slot(sid, pid, stem, name, options, g):
    gd = g[pid]
    assert len(gd['notes']) == len(options), (pid, len(gd['notes']), len(options))
    assert len(gd.get('lessons', [])) in (0, len(options)), pid
    opts = []
    for i, o in enumerate(options):
        im = Image.open(io.BytesIO(show('src/Spanda/Resources/parts_collectibles/%s_%d.jpg' % (stem, i), True))).convert('RGB')
        im = im.resize((800, round(800 * im.height / im.width)), Image.LANCZOS)
        img = 'img/parts/%s_%d.webp' % (stem, i)  # WebP: about half the weight of the old JPEGs
        im.save(os.path.join(W, img), 'WEBP', quality=80)
        use, bg = lesson(gd['lessons'][i]) if gd.get('lessons') else ('', '')
        opts.append({'name': o, 'img': img + '?v=' + HASH,  # the art changes under the same names, so bust the cache
                      'note': gd['notes'][i], 'use': use, 'bg': bg, 'w': im.width, 'h': im.height})
    return {'id': sid, 'name': name, 'guide': gd['about'], 'options': opts}


cg = guides(body('CatalogSpec compressorCatalogSpec'))
SENSE, CURVE, GRAB, LETGO, COLOUR = names('kSense'), names('kCurve'), names('kGrab'), names('kLetGo'), names('kColour')
comp = [
    slot('sense', 'compTestSense', 'comp_sense', 'Sense', SENSE, cg),
    slot('curve', 'compTestCurve', 'comp_curve', 'Curve', CURVE, cg),
    slot('grab', 'compTestGrab', 'comp_grab', 'Grab', GRAB, cg),
    slot('letgo', 'compTestLetGo', 'comp_letgo', 'Let go', LETGO, cg),
    slot('colour', 'compTestColour', 'comp_colour', 'Colour', COLOUR, cg),
    slot('place', 'compTestColourPlace', 'comp_place', 'Colour place', ['After gain', 'Before detector'], cg),
    slot('driver', 'compTestColourDriver', 'comp_driver', 'Colour driver', ['Input', 'Gain reduction', 'Output level', 'Knee position'], cg),
]

# compressor recipes: the unit starting points (UnitRecipe in PartsBasketCompressor.h), then the kRecipes table
ENUM = {k: re.findall(r'(\w+)(?: = 0)?', re.search(r'enum class %s : std::uint32_t \{(.*?)\}' % k, pb)[1])
        for k in ['BasketSense', 'BasketCurve', 'BasketGrab', 'BasketLetGo', 'BasketColour', 'BasketColourPlace', 'BasketColourDriver']}
FIELDS = [('sense', 'BasketSense'), ('curve', 'BasketCurve'), ('grab', 'BasketGrab'), ('letGo', 'BasketLetGo'),
          ('colour', 'BasketColour'), ('colourPlace', 'BasketColourPlace'), ('colourDriver', 'BasketColourDriver')]
crec_src = body('std::vector<CatalogPreset> compressorRecipes')
recipes = []
for name, unit in re.findall(r'std::pair\{ "([^"]+)", U::(\w+) \}', crec_src):
    case = re.search(r'case UnitRecipe::%s:(.*?)break;' % unit, pb, re.S)[1]
    vals = []
    for f, enum in FIELDS:
        m = re.search(r'p\.%s = %s::(\w+);' % (f, enum), case)
        vals.append(ENUM[enum].index(m[1]) if m else 0)
    recipes.append([name, vals])
for m in re.finditer(r'\{ "([^"]+)", ((?:\d+, ){7})', crec_src):
    recipes.append([m[1], [int(x) for x in m[2].split(',')[:7]]])

eg = guides(body('CatalogSpec eqCatalogSpec'))
shelf, bell = names('kShelfPart'), names('kBellPart')
eq = [
    slot('low', 'eqPartLow', 'eq_low', 'Low band', shelf, eg),
    slot('lowmid', 'eqPartLowMid', 'eq_lowmid', 'Low-mid band', bell, eg),
    slot('highmid', 'eqPartHighMid', 'eq_highmid', 'High-mid band', bell, eg),
    slot('high', 'eqPartHigh', 'eq_high', 'High band', shelf, eg),
]
erec = [[m[1], [int(m[2]), int(m[3]), int(m[4]), int(m[5])]]
        for m in re.finditer(r'\{ "([^"]+)", (\d+), (\d+), (\d+), (\d+), (\d+) \}', body('std::vector<CatalogPreset> eqRecipes'))
        if m[6] == '0']  # the site has no output-ceiling control, so it lists only the recipes that leave it off

# Rows a pick makes unused (rowUnused in PartsBasketCompressor.h) as [slot, other slot, values, why]; the first match wins.
S, C, G, L, K, P, D = range(7)
loop = [SENSE.index('Tube loop'), SENSE.index('Level follow')]
own = 'This sense sets this itself; Release sets how fast it lets go.'
rect = 'The Rectifier sense sets its own grab and let-go; Release sets how fast it drains.'
cell, bite, knock, clean = COLOUR.index('Tube cell'), COLOUR.index('Tube bite'), COLOUR.index('Knock'), COLOUR.index('Clean')
unused = [[G, S, loop, own], [L, S, loop, own], [C, S, loop, own],
          [G, S, [SENSE.index('Rectifier')], rect], [L, S, [SENSE.index('Rectifier')], rect],
          [C, G, [GRAB.index('Knock')], 'The Knock grab brings its own curve.'],
          [P, K, [cell], 'The Tube cell colour always acts on the input, ahead of the gain.'],
          [P, K, [bite], 'The Tube bite colour always acts on the input, ahead of the gain.'],
          [D, K, [cell], 'The Tube cell colour follows the input level.'],
          [D, K, [bite], 'The Tube bite colour follows the input level and the gain reduction.'],
          [P, K, [clean], 'No colour is picked.'], [P, K, [knock], 'The Knock colour sets its own drive.'],
          [D, K, [clean], 'No colour is picked.'], [D, K, [knock], 'The Knock colour sets its own drive.']]

out = {
    'comp': {'tab': 'Compressor', 'slots': comp,
             'note': "Threshold, Ratio, Knee, Attack, Release and Makeup stay on the panel. If a part sets one of them, it locks it there.. that's the part doing its job.",
             'default': [1, 1, 0, 0, 0, 0, 0], 'recipes': recipes, 'unused': unused},
    'eq': {'tab': 'EQ', 'slots': eq,
           'note': 'Frequency, Gain, Q and the shelf switches stay on the panel. Each band takes its own part, so go wild.',
           'default': [0, 0, 0, 0], 'recipes': erec},
}
json.dump(out, open(os.path.join(W, 'parts.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('ok', REF, subprocess.run(['git', '-C', REPO, 'rev-parse', '--short', REF], capture_output=True, text=True).stdout.strip(),
      'comp', [len(s['options']) for s in comp], 'eq', [len(s['options']) for s in eq], len(recipes), 'comp recipes', len(erec), 'eq recipes')
