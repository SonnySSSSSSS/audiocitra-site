// "Try it on your own audio": a plug-in's own engine (WebAssembly) in an AudioWorklet. <div data-tryit="akasa|lahari">.
// Limits: one file at a time, up to 25 MB, the first 15 seconds only, twelve chosen factory presets (and Mix where the preset
// does not set it), no export or download. The file is decoded and played in this browser; it is never uploaded.
(() => {
  const box = document.querySelector("[data-tryit]"); if (!box) return;
  const MAX_S = 15, MAX_MB = 25, V = "?v=try8";
  // built-in sources (audio/try/, tools/make_tryit_samples.py, from Splice packs). Each engine lists the ones that suit it, most typical first.
  const SAMPLES = { "guitar-riff": "Guitar chords", "guitar-line": "Guitar line", "guitar-clean": "Clean guitar arp", nylon: "Nylon guitar",
    bass: "Bass", "synth-bass": "Synth bass", drums: "Drums", "rock-drums": "Rock drums", "synth-lead": "Synth lead", wurlitzer: "Wurlitzer",
    rhodes: "Rhodes", pad: "Pad", pluck: "Synth pluck", vocal: "Vocal", cello: "Cello", sax: "Sax", flute: "Flute" };
  // per engine: the glue's factory, the C API prefix, and twelve presets [index in the engine's table, category, name].
  const ENGINES = {
    akasa: { mod: "AkasaModule", samples: ["vocal", "sax", "drums", "cello", "nylon", "rhodes"], mix: true, name: "Ākāśa", presets: [
      [0, "Halls", "Grand Hall"], [5, "Halls", "Hall (Vayu)"], [6, "Rooms", "Studio Room"], [10, "Chambers", "Stone Chamber"],
      [13, "Plates", "Steel Sheet"], [17, "Plates", "Deep Sheet"], [21, "Ambience", "Short Ambience"], [23, "Creative", "Ensemble Echo"],
      [26, "Creative", "Backward Room"], [29, "Creative", "Shimmer Hall"], [33, "Creative", "Slap Echo (Vayu)"], [38, "Layered", "Room, Sheet, Hall"]] },
    // Shunya: the Akasa engine built as Shunya (synthlab #34), Mandapa left out; presets keep Mix as Akasa's do
    shunya: { mod: "AkasaModule", samples: ["vocal", "cello", "nylon", "sax", "flute", "drums"], prefix: "akasa", mix: true, name: "Shunya", presets: [
      [0, "Halls", "Hall (Chatur)"], [1, "Halls", "Hall A (Kosha)"], [3, "Halls", "Concert Hall (Vistara)"], [6, "Halls", "Cathedral (Vistara)"],
      [20, "Rooms", "Compact Room (Chatur)"], [22, "Rooms", "Chamber A (Kosha)"], [29, "Plates", "Sheet (Kosha)"], [30, "Plates", "Classic Plate (Vistara)"],
      [38, "Plates", "Vocal Plate (Vistara)"], [48, "Ambience", "Vast Air (Vistara)"], [52, "Creative", "Echo (Kosha)"], [57, "Creative", "Car Park (Vistara)"]] },
    // Galana: no global Mix (each preset sets its stages' mixes); its web Mix is a blend after the engine that a preset resets
    // to 100 %, so no slider. Square Pluck Bass (11) is left out: it parts from the plug-in in wasm (galana #5).
    galana: { mod: "GalanaModule", samples: ["synth-lead", "synth-bass", "drums", "guitar-clean", "pad", "pluck"], mix: false, name: "Gālana", presets: [
      [0, "Bass Guitar", "Dub Bass"], [6, "Bass Synth", "Acid Squelch"], [12, "Bass Synth", "Sub Wobble"], [14, "Drums", "Drum Chords"],
      [18, "Drums", "Lo-Fi Break"], [27, "Guitar", "Auto-Wah Funk"], [31, "Guitar", "Shoegaze Wash"], [34, "Guitar", "Talk Box"],
      [40, "Keys & Synth", "Rhodes Wah"], [42, "Sound Design", "Barber Pole"], [50, "Sound Design", "Water Drops"], [56, "Vocals", "Vowel Morph"]] },
    // Agni: the preset's Mix is part of the sound (as Lahari). No capture slot or cab IR in the web build; no factory preset uses them.
    agni: { mod: "AgniModule", samples: ["guitar-riff", "guitar-line", "synth-lead", "synth-bass", "rock-drums", "wurlitzer"], mix: false, name: "Agni", presets: [
      [0, "Bass Guitar", "Bass Drive Blend"], [1, "Bass Guitar", "Growl Grit"], [3, "Bass Synth", "Acid Bite"], [6, "Drums", "Drum Bus Crunch"],
      [9, "Guitar", "Classic Fuzz"], [11, "Guitar", "Metal Rhythm"], [13, "Guitar", "Push Overdrive"], [14, "Keys & Synth", "Rhodes Bark"],
      [16, "Keys & Synth", "Wurli Tape"], [18, "Sound Design", "Feedback Drone"], [21, "Vocals", "Megaphone"], [23, "Vocals", "Vocal Warmth"]] },
    // a Lahari preset sets its own Mix (part of the sound), so its player has no Mix slider
    lahari: { mod: "LahariModule", samples: ["guitar-clean", "rhodes", "pad", "synth-lead", "vocal", "nylon"], mix: false, name: "Lahari", presets: [
      [0, "Guitar", "Soft Stream"], [1, "Guitar", "Thick Ensemble"], [2, "Guitar", "Jet Sweep"], [3, "Guitar", "Spiral Funk"],
      [5, "Bass", "Bass Chorus"], [8, "Keys & Synth", "Wide Ripple"], [10, "Keys & Synth", "Ensemble Pad"], [13, "Keys & Synth", "Whirl Rotor"],
      [16, "Vocals", "Vocal Doubler"], [18, "Drums", "Hat Phaser"], [21, "Sound Design", "Metal Comb"], [24, "Sound Design", "Dark Celeste"]] },
  };
  const key = box.dataset.tryit, E = ENGINES[key]; if (!E) return;
  const $ = s => box.querySelector(s);
  const file = $("input[type=file]"), status = $(".try-status"), ctl = $(".try-ctl");
  const sel = $("select"), mix = $("input[type=range]"), mixv = $(".try-mixv"), play = $(".try-play"), ab = $(".try-ab");
  const groups = {};
  for (const [i, cat, name] of E.presets) {
    const g = groups[cat] || (groups[cat] = sel.appendChild(Object.assign(document.createElement("optgroup"), { label: cat })));
    g.append(new Option(name, i));
  }
  if (!E.mix) mix.closest(".try-f").hidden = true;
  const sampleBox = $(".try-samples");
  const sampleBtns = (E.samples || []).map(k => {
    const b = Object.assign(document.createElement("button"), { type: "button", className: "btn", textContent: SAMPLES[k] });
    b.setAttribute("aria-pressed", "false"); b.dataset.k = k; sampleBox.append(b); return b;
  });
  const abText = () => { ab.textContent = dry ? `Dry (tap for ${E.name})` : `${E.name} (tap for dry)`; };
  if (!window.AudioWorkletNode || !window.WebAssembly) { status.textContent = "This browser can't run the player. Try a current Chrome, Edge, Firefox or Safari."; file.disabled = true; return; }

  let ctx, node, src, buf, playing = false, dry = false, loading;
  abText();
  const say = t => { status.textContent = t; };

  async function boot() {
    ctx = new AudioContext({ sampleRate: 48000, latencyHint: "playback" });
    const [glue, worklet, wasm] = await Promise.all([
      fetch(`engine/${key}.js${V}`).then(r => r.text()),
      fetch("engine/worklet.js" + V).then(r => r.text()),
      fetch(`engine/${key}.wasm${V}`).then(r => r.arrayBuffer())]);
    const url = URL.createObjectURL(new Blob([glue, `\nconst ENGINE_MODULE = ${E.mod};\n`, worklet], { type: "text/javascript" }));
    await ctx.audioWorklet.addModule(url); URL.revokeObjectURL(url);
    node = new AudioWorkletNode(ctx, "engine", { numberOfInputs: 1, numberOfOutputs: 1, outputChannelCount: [2],
      channelCount: 2, channelCountMode: "explicit", channelInterpretation: "speakers", processorOptions: { wasm, prefix: E.prefix || key } });
    await new Promise((ok, bad) => { node.port.onmessage = e => e.data.ready ? ok() : bad(new Error(e.data.error)); });
    node.connect(ctx.destination);
    send();
  }
  // dry: Mix 0. Back to wet: the preset again (Lahari's own Mix comes with it), then the slider's Mix where there is one.
  const send = () => {
    if (!node) return;
    const m = { preset: +sel.value };
    if (dry) m.mix = 0; else if (E.mix) m.mix = +mix.value;
    node.port.postMessage(m);
  };

  const mark = k => sampleBtns.forEach(b => b.setAttribute("aria-pressed", b.dataset.k === k));
  sampleBtns.forEach(b => b.addEventListener("click", () => {
    file.value = ""; mark(b.dataset.k);
    use(SAMPLES[b.dataset.k] + " (sample)", () => fetch(`audio/try/${b.dataset.k}.mp3${V}`).then(r => { if (!r.ok) throw new Error(r.status); return r.arrayBuffer(); }), "the sample");
  }));
  file.addEventListener("change", () => {
    const f = file.files[0]; if (!f) return;
    mark(null);
    if (f.size > MAX_MB * 1048576) { stop(); say(`That file is over ${MAX_MB} MB. Trim it or export a shorter clip.`); return; }
    use(f.name, () => f.arrayBuffer(), "your file");
  });
  async function use(label, bytes, what) {
    stop();
    say(`Loading the engine and ${what}…`);
    try {
      loading = loading || boot(); await loading;
      const raw = await ctx.decodeAudioData(await bytes());
      const n = Math.min(raw.length, MAX_S * ctx.sampleRate), ch = Math.min(2, raw.numberOfChannels);
      buf = ctx.createBuffer(ch, n, ctx.sampleRate);
      let peak = 0;
      for (let c = 0; c < ch; c++) { const d = raw.getChannelData(c).subarray(0, n); buf.copyToChannel(d, c); for (const v of d) peak = Math.max(peak, Math.abs(v)); }
      if (peak < 1e-4) { say("That file is silent."); buf = null; return; }
      const g = 0.5 / peak;                                        // peak to -6 dBFS, so every file starts at a safe level
      for (let c = 0; c < ch; c++) { const d = buf.getChannelData(c); for (let k = 0; k < n; k++) d[k] *= g; }
      const cut = raw.length > n;
      say(`${label.slice(0, 60)} · ${(n / ctx.sampleRate).toFixed(1)} s${cut ? ` (the first ${MAX_S} s)` : ""} · loops until you stop it`);
      ctl.hidden = false; start();
    } catch (e) { say(what === "your file" ? "Couldn't read that file. WAV, MP3, FLAC, OGG or M4A usually work." : "Couldn't load the sample. Try again."); console.error(e); }
  }

  function start() {
    if (!buf) return; stop();
    ctx.resume();
    src = new AudioBufferSourceNode(ctx, { buffer: buf, loop: true }); src.connect(node); src.start();
    playing = true; play.textContent = "Stop"; play.setAttribute("aria-pressed", "true");
  }
  function stop() {
    if (src) { try { src.stop(); } catch {} src.disconnect(); src = null; }
    playing = false; play.textContent = "Play"; play.setAttribute("aria-pressed", "false");
  }
  play.addEventListener("click", () => playing ? stop() : start());
  sel.addEventListener("change", send);
  mix.addEventListener("input", () => { mixv.textContent = mix.value + " %"; if (!dry) node && node.port.postMessage({ mix: +mix.value }); });
  ab.addEventListener("click", () => { dry = !dry; ab.setAttribute("aria-pressed", dry); abText();
    if (E.mix) node && node.port.postMessage({ mix: dry ? 0 : +mix.value });   // Akasa: Mix only, so the tail is not rebuilt
    else send(); });
  document.addEventListener("visibilitychange", () => { if (document.hidden && playing) stop(); });
})();
