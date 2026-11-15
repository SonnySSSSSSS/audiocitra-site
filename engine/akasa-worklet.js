// AudioWorklet processor for the Akasa try-it player. Appended to engine/akasa.js (the Emscripten glue) by tryit.js and loaded
// as one Blob module, so AkasaModule is in scope. The wasm bytes arrive in processorOptions; nothing is fetched in here.
class AkasaProcessor extends AudioWorkletProcessor {
  constructor(opts) {
    super();
    this.ready = false;
    const bytes = opts.processorOptions.wasm;                    // this glue has no wasmBinary path, so instantiate it here
    AkasaModule({ instantiateWasm(info, done) { WebAssembly.instantiate(bytes, info).then(r => done(r.instance)); return {}; } }).then(M => {
      this.M = M;
      this.h = M._akasa_create(sampleRate);
      if (!M._akasa_check_table(this.h)) { this.port.postMessage({ error: "table" }); return; }
      this.pL = M._malloc(128 * 4); this.pR = M._malloc(128 * 4);
      this.ready = true;
      this.port.postMessage({ ready: true });
    }, e => this.port.postMessage({ error: String(e) }));
    this.port.onmessage = e => {
      const d = e.data, M = this.M; if (!this.ready) return;
      if ("preset" in d) M._akasa_load_preset(this.h, d.preset);   // rebuilds the engine: the tail restarts, as in the plug-in
      if ("mix" in d) M._akasa_set_mix(this.h, d.mix);
    };
  }
  process(inputs, outputs) {
    const out = outputs[0]; if (!out || !out.length) return true;
    const n = out[0].length;
    if (!this.ready || n > 128) { for (const c of out) c.fill(0); return true; }
    const inp = inputs[0], M = this.M;
    let heap = M.HEAPF32, l = this.pL >> 2, r = this.pR >> 2;
    if (inp && inp.length) { heap.set(inp[0], l); heap.set(inp[1] || inp[0], r); }
    else { heap.fill(0, l, l + n); heap.fill(0, r, r + n); }
    M._akasa_process(this.h, this.pL, this.pR, n);
    heap = M.HEAPF32;                                            // memory may have grown
    const oL = out[0], oR = out[1] || out[0];
    for (let k = 0; k < n; k++) {                                // hard ceiling at -1 dBFS: nothing louder ever leaves the page
      const a = heap[l + k], b = heap[r + k];
      oL[k] = a > 0.891 ? 0.891 : a < -0.891 ? -0.891 : a;
      oR[k] = b > 0.891 ? 0.891 : b < -0.891 ? -0.891 : b;
    }
    return true;
  }
}
registerProcessor("akasa", AkasaProcessor);
