// "Try it on your own audio": the Akasa engine (WebAssembly, the plug-in's own DSP) in an AudioWorklet.
// Limits: one file at a time, up to 25 MB, the first 15 seconds only, factory presets and Mix only, no export or download.
// The file is decoded and played in this browser; it is never uploaded.
(() => {
  const box = document.querySelector("[data-tryit]"); if (!box) return;
  const MAX_S = 15, MAX_MB = 25, V = "?v=try2";
  const $ = s => box.querySelector(s);
  const file = $("input[type=file]"), status = $(".try-status"), ctl = $(".try-ctl");
  const sel = $("select"), mix = $("input[type=range]"), mixv = $(".try-mixv"), play = $(".try-play"), ab = $(".try-ab");
  if (!window.AudioWorkletNode || !window.WebAssembly) { status.textContent = "This browser can't run the player. Try a current Chrome, Edge, Firefox or Safari."; file.disabled = true; return; }

  let ctx, node, src, buf, playing = false, dry = false, loading;
  const say = t => { status.textContent = t; };

  async function boot() {
    ctx = new AudioContext({ sampleRate: 48000, latencyHint: "playback" });
    const [glue, worklet, wasm] = await Promise.all([
      fetch("engine/akasa.js" + V).then(r => r.text()),
      fetch("engine/akasa-worklet.js" + V).then(r => r.text()),
      fetch("engine/akasa.wasm" + V).then(r => r.arrayBuffer())]);
    const url = URL.createObjectURL(new Blob([glue, "\n", worklet], { type: "text/javascript" }));
    await ctx.audioWorklet.addModule(url); URL.revokeObjectURL(url);
    node = new AudioWorkletNode(ctx, "akasa", { numberOfInputs: 1, numberOfOutputs: 1, outputChannelCount: [2],
      channelCount: 2, channelCountMode: "explicit", channelInterpretation: "speakers", processorOptions: { wasm } });
    await new Promise((ok, bad) => { node.port.onmessage = e => e.data.ready ? ok() : bad(new Error(e.data.error)); });
    node.connect(ctx.destination);
    send();
  }
  const send = () => node && node.port.postMessage({ preset: +sel.value, mix: dry ? 0 : +mix.value });

  file.addEventListener("change", async () => {
    const f = file.files[0]; if (!f) return;
    stop();
    if (f.size > MAX_MB * 1048576) { say(`That file is over ${MAX_MB} MB. Trim it or export a shorter clip.`); return; }
    say("Loading the engine and decoding your file…");
    try {
      loading = loading || boot(); await loading;
      const raw = await ctx.decodeAudioData(await f.arrayBuffer());
      const n = Math.min(raw.length, MAX_S * ctx.sampleRate), ch = Math.min(2, raw.numberOfChannels);
      buf = ctx.createBuffer(ch, n, ctx.sampleRate);
      let peak = 0;
      for (let c = 0; c < ch; c++) { const d = raw.getChannelData(c).subarray(0, n); buf.copyToChannel(d, c); for (const v of d) peak = Math.max(peak, Math.abs(v)); }
      if (peak < 1e-4) { say("That file is silent."); buf = null; return; }
      const g = 0.5 / peak;                                        // peak to -6 dBFS, so every file starts at a safe level
      for (let c = 0; c < ch; c++) { const d = buf.getChannelData(c); for (let k = 0; k < n; k++) d[k] *= g; }
      const cut = raw.length > n;
      say(`${f.name.slice(0, 60)} · ${(n / ctx.sampleRate).toFixed(1)} s${cut ? ` (the first ${MAX_S} s)` : ""} · loops until you stop it`);
      ctl.hidden = false; start();
    } catch (e) { say("Couldn't read that file. WAV, MP3, FLAC, OGG or M4A usually work."); console.error(e); }
  });

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
  ab.addEventListener("click", () => { dry = !dry; ab.setAttribute("aria-pressed", dry); ab.textContent = dry ? "Dry (tap for Ākāśa)" : "Ākāśa (tap for dry)"; send(); });
  document.addEventListener("visibilitychange", () => { if (document.hidden && playing) stop(); });
})();
