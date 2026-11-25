// Front-page heroes as real-time 3D: a room whose <article> carries data-hero3d="3d/hero/<name>" gets that unit as a model
// (<name>.glb, framed by <name>.json from tools/hero_glb.py) over its still. The unit turns a few degrees toward the pointer
// and eases back when it leaves; on touch screens it sways gently. Live parts (a VFD, meters, a lotus) play the videos named in
// data-live ('{"LIVE_vfd":"3d/hero/lim-vfd"}': .webm and .mp4 beside it) on their emissive texture.
// The still stays the page's image: the model fades in over it only once it has drawn, only in the room that is on, and never
// for reduced motion, without WebGL, or on a slow connection. One model is live at a time; leaving a room pauses its videos.
(() => {
  const rooms = [...document.querySelectorAll(".room[data-hero3d]")]; if (!rooms.length) return;
  const mq = matchMedia("(prefers-reduced-motion: reduce)");
  const slow = () => navigator.connection && (navigator.connection.saveData || /2g/.test(navigator.connection.effectiveType || ""));
  const gl = (() => { try { return !!document.createElement("canvas").getContext("webgl2"); } catch { return false; } })();
  if (!gl) return;
  const hover = matchMedia("(hover: hover) and (pointer: fine)").matches;
  const TURN = 12, TILT = 5;              // the most the unit turns (left-right) and tilts (up-down) toward the pointer, degrees
  let mv = null;                          // the model-viewer module, loaded on first need
  const loadMV = () => mv || (mv = import("https://cdn.jsdelivr.net/npm/@google/model-viewer@3.5.0/dist/model-viewer.min.js"));

  const state = new Map();                // room -> { wrap, el, cam, videos, ready }

  // The model's box copies the still's: same rectangle, mask and filter; inside it the canvas has the still's own 16:9 shape,
  // scaled and offset as object-fit: cover with the still's object-position would place it, so the camera's field of view is
  // exactly the render's.
  function fit(room, s) {
    const img = room.querySelector(":scope > img"), cs = getComputedStyle(img);
    const rr = room.getBoundingClientRect(), ir = img.getBoundingClientRect();
    Object.assign(s.wrap.style, { left: ir.left - rr.left + "px", top: ir.top - rr.top + "px", width: ir.width + "px", height: ir.height + "px",
      maskImage: cs.maskImage, webkitMaskImage: cs.webkitMaskImage, filter: cs.filter });
    const a = s.cam.aspect, k = Math.max(ir.width / a, ir.height);                  // cover: the canvas height
    const w = k * a, h = k, [px, py] = cs.objectPosition.split(" ").map(v => parseFloat(v) / 100);
    Object.assign(s.el.style, { width: w + "px", height: h + "px", left: (ir.width - w) * (isNaN(px) ? .5 : px) + "px",
      top: (ir.height - h) * (isNaN(py) ? .5 : py) + "px" });
  }

  const orbit = (c, dt = 0, dp = 0) => `${c.theta_deg + dt}deg ${c.phi_deg + dp}deg ${c.radius}m`;

  async function build(room) {
    if (state.has(room)) return state.get(room);
    const base = room.dataset.hero3d, s = { ready: false, videos: [] }; state.set(room, s);
    const [cam] = await Promise.all([fetch(base + ".json").then(r => r.json()).then(j => j.camera), loadMV()]);
    s.cam = cam;
    s.wrap = document.createElement("div"); s.wrap.className = "h3d"; s.wrap.setAttribute("aria-hidden", "true");
    const el = s.el = document.createElement("model-viewer");
    el.setAttribute("src", base + ".glb");
    el.setAttribute("camera-target", cam.target.map(v => v + "m").join(" "));
    el.setAttribute("camera-orbit", orbit(cam));
    el.setAttribute("field-of-view", cam.vfov_deg + "deg");
    el.setAttribute("min-field-of-view", cam.vfov_deg + "deg"); el.setAttribute("max-field-of-view", cam.vfov_deg + "deg");
    el.setAttribute("min-camera-orbit", "auto auto " + cam.radius * 0.5 + "m"); el.setAttribute("max-camera-orbit", "auto auto " + cam.radius * 2 + "m");
    el.setAttribute("interpolation-decay", "140");
    el.setAttribute("tone-mapping", "agx");
    el.setAttribute("exposure", String(Math.pow(2, cam.exposure || 0)));
    el.setAttribute("environment-image", room.dataset.hero3dEnv || base + "_env.hdr");
    el.setAttribute("shadow-intensity", "0"); el.setAttribute("interaction-prompt", "none");
    el.setAttribute("disable-zoom", ""); el.setAttribute("disable-pan", ""); el.setAttribute("disable-tap", "");
    el.setAttribute("loading", "eager"); el.setAttribute("reveal", "auto");
    s.wrap.append(el);
    room.querySelector(":scope > img").after(s.wrap);
    fit(room, s);
    el.addEventListener("load", async () => {
      const live = JSON.parse(room.dataset.live || "{}");
      for (const [mat, src] of Object.entries(live)) {
        const m = el.model.getMaterialByName(mat); if (!m) continue;
        const ext = document.createElement("video").canPlayType('video/webm; codecs="vp9"') ? ".webm" : ".mp4";
        const tex = el.createVideoTexture(src + ext);
        m.emissiveTexture.setTexture(tex);
        s.videos.push(tex.source?.element || tex.source);
      }
      // the model shows only once it has drawn a frame, so the still is never swapped for a blank canvas
      requestAnimationFrame(() => requestAnimationFrame(() => { s.ready = true; if (room.classList.contains("on")) on(room); }));
    }, { once: true });
    return s;
  }

  function on(room) {
    const s = state.get(room); if (!s || !s.ready || !room.classList.contains("on")) return;
    s.wrap.classList.add("live"); s.videos.forEach(v => v && v.play && v.play().catch(() => {}));
  }
  function off(room) {
    const s = state.get(room); if (!s || !s.wrap) return;
    s.wrap.classList.remove("live"); s.videos.forEach(v => v && v.pause && v.pause());
    if (s.cam) s.el.cameraOrbit = orbit(s.cam);
  }

  // pointer: the unit turns toward it (azimuth for left-right, polar for up-down), back to the render's pose on leave
  rooms.forEach(room => {
    room.addEventListener("pointermove", e => {
      const s = state.get(room); if (!s || !s.ready || e.pointerType !== "mouse") return;
      const r = s.wrap.getBoundingClientRect();
      const x = Math.max(-1, Math.min(1, (e.clientX - r.left) / r.width * 2 - 1)), y = Math.max(-1, Math.min(1, (e.clientY - r.top) / r.height * 2 - 1));
      s.el.cameraOrbit = orbit(s.cam, -x * TURN, -y * TILT);
    });
    room.addEventListener("pointerleave", () => { const s = state.get(room); if (s && s.cam) s.el.cameraOrbit = orbit(s.cam); });
  });

  // touch screens: a slow sway, only while the room is on and on screen
  let t0 = 0, raf = 0;
  function sway(t) {
    const room = document.querySelector(".room.on[data-hero3d]"), s = room && state.get(room);
    if (s && s.ready && !document.hidden) s.el.cameraOrbit = orbit(s.cam, Math.sin((t - t0) / 3200) * TURN * 0.4, Math.sin((t - t0) / 4700) * TILT * 0.3);
    raf = requestAnimationFrame(sway);
  }

  function sync() {
    if (mq.matches || slow()) { rooms.forEach(off); return; }
    rooms.forEach(room => {
      if (room.classList.contains("on")) build(room).then(() => on(room));
      else off(room);
    });
  }
  const mo = new MutationObserver(sync);          // the rooms' own class only (rooms.js toggles "on"), never their contents
  rooms.forEach(r => mo.observe(r, { attributes: true, attributeFilter: ["class"] }));
  addEventListener("resize", () => state.forEach((s, room) => s.el && s.cam && fit(room, s)));
  mq.addEventListener?.("change", sync);
  document.addEventListener("visibilitychange", () => { const r = document.querySelector(".room.on[data-hero3d]"); if (r) document.hidden ? off(r) : on(r); });
  // start after the page's own load, so the still stays the largest paint
  const go = () => { sync(); if (!hover) raf = requestAnimationFrame(sway); };
  document.readyState === "complete" ? setTimeout(go, 300) : addEventListener("load", () => setTimeout(go, 300), { once: true });
})();
