// Shared nav/footer, Spanda module tabs, skin compare sliders, listen players, teardown, parts builder.
(() => {
  const pages = [["spanda.html","Spanda"],["galana.html","Gālana"],["agni.html","Agni"],["akasa.html","Ākāśa"],["shunya.html","Shunya"],["lahari.html","Lahari"]];
  // "" and "/" are the index, "spanda" or "spanda/" are spanda.html
  let here = location.pathname.replace(/\/+$/, "").split("/").pop() || "index.html";
  if (!/\./.test(here)) here += ".html";
  const nav = document.createElement("nav");
  nav.setAttribute("aria-label", "Main");
  nav.innerHTML = `${document.getElementById("main") ? '<a class="skip" href="#main">Skip to content</a>' : ""}<div class="wrap"><a class="logo" href="index.html">AUDIO CITRA</a><ul>${
    pages.map(([h,t]) => `<li><a href="${h}"${h===here?' aria-current="page"':""}>${t}</a></li>`).join("")}</ul></div>`;
  document.body.prepend(nav);
  const foot = document.createElement("footer");
  foot.innerHTML = `<div class="wrap"><span>Audio Citra · VST3 · Windows</span><span><a href="buy.html">Buy</a> · <a href="refund.html">Refunds</a> · <a href="terms.html">Terms</a> · <a href="privacy.html">Privacy</a> · <a href="credits.html">Credits</a></span></div>`;
  document.body.append(foot);

  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const pad2 = i => String(i + 1).padStart(2, "0");
  const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  // escape everything, then allow only <em> and </em> back in
  const escEm = s => esc(s).replace(/&lt;(\/?)em&gt;/g, "<$1em>");
  const escRe = s => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

  // A section whose data failed or is empty goes away together with the links that point to it.
  const drop = (el, box = el.closest("section") || el) => {
    const id = box.id || el.id;
    box.remove();
    if (id) document.querySelectorAll(`a[href="#${id}"]`).forEach(a => { a.hidden = true; });
  };
  const getJson = async url => { const r = await fetch(url); if (!r.ok) throw new Error(r.status); return r.json(); };

  // Module tabs: tablist semantics, roving tabindex, arrow/Home/End keys.
  document.querySelectorAll("[data-tabs]").forEach(group => {
    const list = group.querySelector(".tabs"); if (!list) return;
    const btns = [...list.querySelectorAll("button")];
    const panels = btns.map(b => document.getElementById(b.dataset.for));
    list.setAttribute("role", "tablist");
    btns.forEach((b, i) => {
      b.setAttribute("role", "tab"); b.id ||= `tab-${b.dataset.for}`; b.setAttribute("aria-controls", b.dataset.for);
      if (panels[i]) { panels[i].setAttribute("role", "tabpanel"); panels[i].setAttribute("aria-labelledby", b.id); }
    });
    const activate = (b, focus) => {
      btns.forEach((x, i) => {
        const on = x === b;
        x.setAttribute("aria-selected", on); x.tabIndex = on ? 0 : -1;
        panels[i]?.classList.toggle("on", on);
      });
      if (focus) b.focus();
    };
    activate(btns.find(b => b.getAttribute("aria-selected") === "true") || btns[0], false);
    btns.forEach(b => b.addEventListener("click", () => activate(b, false)));
    list.addEventListener("keydown", e => {
      const i = btns.indexOf(document.activeElement); if (i < 0) return;
      const to = { ArrowRight: (i + 1) % btns.length, ArrowLeft: (i - 1 + btns.length) % btns.length, Home: 0, End: btns.length - 1 }[e.key];
      if (to === undefined) return;
      e.preventDefault(); activate(btns[to], true);
    });
  });

  document.querySelectorAll(".compare").forEach(c => {
    const r = c.querySelector("input");
    const set = () => c.style.setProperty("--x", r.value + "%");
    r.addEventListener("input", set); set();
  });

  // Measurements: a grid of analyser plots from meas.json
  document.querySelectorAll("[data-meas]").forEach(async el => {
    try {
      const items = (await getJson("meas.json"))[el.dataset.meas] || [];
      if (!items.length) throw 0;
      el.innerHTML = items.map(m =>
        `<figure class="meas"><a href="${esc(m.src)}" target="_blank" rel="noopener"><img src="${esc(m.src)}" alt="${esc(m.title)}"${m.w ? ` width="${m.w}" height="${m.h}"` : ""} loading="lazy"></a>
         <figcaption><b>${esc(m.title)}</b><span>${esc(m.caption)}</span><small>${esc(m.settings)} · 48 kHz</small></figcaption></figure>`).join("");
    } catch { drop(el); }
  });

  // Listen: dry / processed A/B players from audio/clips.json; switching keeps the playhead
  document.querySelectorAll("[data-listen]").forEach(async el => {
    let clips = [];
    try { clips = (await getJson("audio/clips.json")).filter(c => c.plugin.toLowerCase() === el.dataset.listen); } catch {}
    if (!clips.length) { drop(el); return; }
    const name = el.dataset.name || el.dataset.listen;
    el.innerHTML = clips.map((c, i) => `
      <div class="ab-card" data-i="${i}">
        <button class="play" aria-label="Play ${esc(c.title)}" data-title="${esc(c.title)}">▶</button>
        <div class="ab-meta"><b>${esc(c.title)}</b><small>${esc(c.settings_summary)}</small></div>
        <div class="seg" role="group" aria-label="Dry or processed, ${esc(c.title)}"><button aria-pressed="true" data-k="dry">Dry</button><button aria-pressed="false" data-k="wet">${esc(name)}</button></div>
        <audio preload="none" src="audio/${esc(c.dry)}"></audio><audio preload="none" src="audio/${esc(c.wet)}"></audio>
      </div>`).join("");
    const credits = [...new Set(clips.map(c => c.credit).filter(Boolean))];
    if (credits.length) el.insertAdjacentHTML("beforeend", `<p class="cap">${credits.map(esc).join(" · ")}</p>`);
    const stopAll = except => document.querySelectorAll(".ab-card").forEach(k => {
      if (k !== except) { k.querySelectorAll("audio").forEach(a => a.pause()); k._show?.(false); }
    });
    el.querySelectorAll(".ab-card").forEach(card => {
      const [dry, wet] = card.querySelectorAll("audio"); let cur = dry, warmed = false;
      const play = card.querySelector(".play");
      const show = on => { play.textContent = on ? "❚❚" : "▶"; play.setAttribute("aria-label", `${on ? "Pause" : "Play"} ${play.dataset.title}`); };
      card._show = show;
      const start = a => { const p = a.play(); if (p && p.catch) p.catch(() => { if (a === cur) show(false); }); };
      play.addEventListener("click", () => {
        if (cur.paused) {
          stopAll(card);
          if (!warmed) { warmed = true; dry.preload = wet.preload = "auto"; }  // both ready so Dry/Wet switching has no gap
          start(cur); show(true);
        } else { cur.pause(); show(false); }
      });
      [dry, wet].forEach(a => { a.addEventListener("ended", () => show(false)); a.addEventListener("error", () => { if (a === cur) show(false); }); });
      card.querySelectorAll(".seg button").forEach(b => b.addEventListener("click", () => {
        const next = b.dataset.k === "wet" ? wet : dry; if (next === cur) return;
        card.querySelectorAll(".seg button").forEach(x => x.setAttribute("aria-pressed", x === b));
        const playing = !cur.paused, t = cur.currentTime; cur.pause();
        try { next.currentTime = t; } catch {}
        cur = next; if (playing) start(next);
      }));
    });
  });

  // Letters flicker through random glyphs, then settle left to right. The real text stays in a
  // visually hidden span for assistive tech; only the aria-hidden copy animates.
  const scramble = (node, text) => {
    clearInterval(node._t);
    if (reduce) { node.textContent = text; return; }
    node.innerHTML = `<span class="sr"></span><span class="scr" aria-hidden="true"></span>`;
    const real = node.firstChild, vis = node.lastChild;
    real.textContent = text; vis.textContent = text;
    const glyphs = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#%&";
    let f = 0;
    node._t = setInterval(() => {
      const keep = Math.floor(f / 12 * text.length);
      vis.textContent = [...text].map((c, i) => i < keep || c === " " ? c : glyphs[Math.random() * glyphs.length | 0]).join("");
      if (++f > 12) { clearInterval(node._t); vis.textContent = text; }
    }, 28);
  };

  // Blueprint drawings for teardown layers without a render: 320 x 180, in the page accent.
  const blueprint = (() => {
    const X0 = 22, X1 = 298, Y0 = 22, Y1 = 158;
    const xy = (t, v) => `${(X0 + t * (X1 - X0)).toFixed(1)},${(Y1 - Math.min(1, Math.max(0, v)) * (Y1 - Y0)).toFixed(1)}`;
    const plot = (fn, n = 120) => Array.from({ length: n + 1 }, (_, i) => (i ? "L" : "M") + xy(i / n, fn(i / n))).join("");
    const path = (d, extra = "") => `<path d="${d}" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round" ${extra}/>`;
    const faint = d => path(d, 'opacity=".35" stroke-dasharray="3 3"');
    const label = (x, y, s, a = "start") => `<text x="${x}" y="${y}" text-anchor="${a}">${s}</text>`;
    const rand = seed => () => ((seed = (seed * 1664525 + 1013904223) >>> 0) / 4294967296);
    const logHz = t => 20 * Math.pow(1000, t);
    const bump = (l, c, w) => Math.exp(-(((l - c) / w) ** 2));
    const db = (d, lo, hi) => (d - lo) / (hi - lo);
    const lp24 = (f, fc, q) => { const w = f / fc; return 40 * Math.log10(1 / Math.sqrt((1 - w * w) ** 2 + (w / q) ** 2)); };
    const taps = (r, n, t0, t1, decay, w = 1.4) => Array.from({ length: n }, () => {
      const t = t0 + r() * (t1 - t0); const h = Math.exp(-decay * (t - t0)) * (0.45 + 0.55 * r());
      return `M${xy(t, 0)}L${xy(t, h * 0.92)}`; }).join("");
    const D = {
      lp: () => path(plot(t => db(lp24(logHz(t), 1000, 1.4), -60, 20))) + label(X1, 34, "LP 24", "end"),
      res: () => [0.7, 1.6, 3.5, 7].map((q, i) => path(plot(t => db(lp24(logHz(t), 1000, q), -60, 22)), `opacity="${0.35 + i * 0.22}"`)).join("") + label(X1, 34, "RES ↑", "end"),
      comb: () => faint(plot(t => db(20 * Math.log10(Math.sqrt(1 + 1.4 * Math.cos(2 * Math.PI * 9 * t) + 0.49)), -14, 12))) +
                  path(plot(t => db(20 * Math.log10(1 / Math.sqrt(1 - 1.4 * Math.cos(2 * Math.PI * 9 * t) + 0.49)), -14, 12), 360)) + label(X1, 34, "FF → FB", "end"),
      slots: () => ["FILTER", "CHORUS", "DELAY"].map((s, i) => { const x = 26 + i * 98; return `<rect x="${x}" y="62" width="76" height="56" rx="6" fill="none" stroke="currentColor" stroke-width="1.6"/>` +
                  label(x + 38, 94, s, "middle") + `<circle cx="${x + 30}" cy="70" r="1.5" fill="currentColor"/><circle cx="${x + 38}" cy="70" r="1.5" fill="currentColor"/><circle cx="${x + 46}" cy="70" r="1.5" fill="currentColor"/>` +
                  (i < 2 ? path(`M${x + 80},90L${x + 94},90M${x + 89},85L${x + 94},90L${x + 89},95`) : ""); }).join("") + label(160, 146, "ANY OF SIX ORDERS", "middle"),
      io: () => { const z = db(0, -48, 8); return faint(`M${xy(0, z)}L${xy(1, z)}`) + label(X0, 44, "0 dB") +
                  path(plot(t => db(lp24(logHz(t), 400, 0.707), -48, 8))) +
                  path(plot(t => { const w = logHz(t) / 5000; return db(40 * Math.log10(w * w / Math.sqrt((1 - w * w) ** 2 + 2 * w * w)), -48, 8); })) +
                  path(plot(t => { const w = logHz(t) / 1400; return db(20 * Math.log10((w / 0.9) / Math.sqrt((1 - w * w) ** 2 + (w / 0.9) ** 2)), -48, 8); })) +
                  label(70, 150, "LP") + label(160, 150, "BP", "middle") + label(X1, 150, "HP", "end"); },
      shape: () => faint(plot(t => t)) + path(plot(t => 0.5 + 0.5 * Math.tanh(3 * (2 * t - 1)) / Math.tanh(3))) + label(X1, 150, "IN →", "end") + label(X0, 34, "OUT"),
      shape2: () => faint(plot(t => 0.08 + 0.84 * Math.abs(2 * t - 1))) +
                  path(plot(t => { const x = 2 * t - 1; return 0.5 + 0.5 * (x > 0 ? 0.85 * Math.tanh(4 * x) / Math.tanh(4) : Math.tanh(1.6 * x) / Math.tanh(1.6)); })) +
                  label(X1, 34, "DIODE", "end") + label(X1, 150, "RECTIFY", "end"),
      routing: () => { const box = (x, y, s) => `<rect x="${x}" y="${y}" width="52" height="26" rx="5" fill="none" stroke="currentColor" stroke-width="1.6"/>` + label(x + 26, y + 17, s, "middle");
                  return box(110, 40, "A") + box(186, 40, "B") + box(148, 100, "A") + box(148, 136, "B") +
                    path("M30,53L110,53M162,53L186,53M238,53L290,53") +
                    path("M30,131L110,131M110,113L110,149M110,113L148,113M110,149L148,149M200,113L238,113M200,149L238,149M238,113L238,149M238,131L290,131") +
                    faint("M238,46C262,14 86,14 110,46") + label(174, 22, "FEEDBACK", "middle") + label(30, 45, "SERIAL") + label(30, 123, "PARALLEL"); },
      alias: () => { const r = rand(7); let s = ""; [0.22, 0.5, 0.78].forEach((t, i) => s += path(`M${xy(t, 0)}L${xy(t, 0.92 - i * 0.28)}`, 'stroke-width="3"'));
                  for (let i = 0; i < 14; i++) { const t = 0.05 + r() * 0.9; s += faint(`M${xy(t, 0)}L${xy(t, 0.12 + r() * 0.42)}`); }
                  const f = 0.08; return s + path(`M${xy(0, f)}L${xy(1, f)}`, 'opacity=".6"') + label(X1, 136, "8x", "end") + label(X1, 34, "1x", "end"); },
      capture: () => faint(plot(t => 0.5 + 0.42 * Math.sin(4 * Math.PI * t))) + path(plot(t => 0.5 + 0.42 * Math.tanh(2.6 * Math.sin(4 * Math.PI * t) + 0.5) / Math.tanh(3.1), 200)) + label(X1, 34, "CAPTURE", "end"),
      cab: () => path(plot(t => { const l = Math.log10(logHz(t)); return db(4 * bump(l, 2.05, 0.12) + 3 * bump(l, 3.3, 0.15) - (l > 3.6 ? (l - 3.6) * 70 : 0) - (l < 1.85 ? (1.85 - l) * 40 : 0), -36, 10); })) +
                  faint(plot(t => { const l = Math.log10(logHz(t)); return db(2 * bump(l, 2.3, 0.2) + 4 * bump(l, 3.45, 0.1) - (l > 3.7 ? (l - 3.7) * 60 : 0) - (l < 1.9 ? (1.9 - l) * 40 : 0), -36, 10); })) +
                  label(X0, 34, "CAB A") + label(X1, 34, "CAB B", "end"),
      conv: () => faint(plot(t => 0.5 + 0.42 * Math.sin(2 * Math.PI * t))) + path(plot(t => 0.5 + Math.round(0.42 * Math.sin(2 * Math.PI * (Math.floor(t * 28) / 28)) * 7) / 7 * 1, 560), 'stroke-linejoin="miter"') + label(X1, 34, "WORD LENGTH", "end"),
      early: () => path(`M${xy(0.04, 0)}L${xy(0.04, 0.95)}`, 'stroke-width="2.4"') + path(taps(rand(3), 9, 0.1, 0.5, 3.2)) + label(X0 + 4, 34, "DIRECT") + label(X1, 34, "EARLY", "end"),
      diffuse: () => path(taps(rand(11), 70, 0.08, 0.92, 2.4), 'stroke-width="1.1"') + label(X1, 34, "DENSITY", "end"),
      tail: () => { const r = rand(5); let s = ""; for (let i = 0; i < 150; i++) { const t = i / 150, h = Math.exp(-4 * t) * (0.25 + 0.75 * r()); s += `M${xy(t, 0.5 - h * 0.46)}L${xy(t, 0.5 + h * 0.46)}`; }
                  return path(s, 'stroke-width="1" opacity=".75"') + path(plot(t => 0.5 + 0.46 * Math.exp(-4 * t))) + path(plot(t => 0.5 - 0.46 * Math.exp(-4 * t))) + label(X1, 34, "DECAY", "end"); },
      tail2: () => path(plot(t => 0.08 + 0.86 * Math.exp(-2.4 * t))) + path(plot(t => 0.08 + 0.86 * Math.exp(-6.5 * t)), 'stroke-dasharray="5 3"') + label(176, 92, "LOW") + label(70, 134, "HIGH"),
      eq: () => { const sig = x => 1 / (1 + Math.exp(-x)); const z = db(0, -12, 12);
                  return faint(`M${xy(0, z)}L${xy(1, z)}`) + path(plot(t => { const l = Math.log10(logHz(t)); return db(4 * (1 - sig((l - 2.1) * 9)) - 3.5 * bump(l, 2.6, 0.16) + 3 * sig((l - 3.9) * 9), -12, 12); })) + label(X1, 34, "WET EQ", "end"); },
      null: () => path(plot(t => 0.72 + 0.2 * Math.sin(6 * Math.PI * t) * Math.exp(-1.5 * t), 200)) + path(plot(t => 0.72 + 0.2 * Math.sin(6 * Math.PI * t) * Math.exp(-1.5 * t), 200), 'opacity=".5" stroke-dasharray="4 4" transform="translate(0 0)"') +
                  path(`M${xy(0, 0.16)}L${xy(1, 0.16)}`) + label(X0, 34, "ORIGINAL + REBUILD") + label(X0, 126, "RESIDUAL"),
      flat: () => path(plot(t => t)) + label(X1, 150, "IN →", "end") + label(X0, 34, "OUT"),
    };
    const grid = Array.from({ length: 15 }, (_, i) => `M${X0 + i * 19.7},${Y0}V${Y1}`).join("") + Array.from({ length: 8 }, (_, i) => `M${X0},${Y0 + i * 19.4}H${X1}`).join("");
    return k => `<svg viewBox="0 0 320 180" aria-hidden="true"><path d="${grid}" stroke="currentColor" stroke-width=".5" opacity=".14"/>${(D[k] || D.flat)()}</svg>`;
  })();

  // Teardown: a pinned stage where scrolling pulls the product apart into its stages,
  // then steps through them one at a time with numbered callouts.
  document.querySelectorAll("[data-teardown]").forEach(async el => {
    let t;
    try { t = (await getJson("teardown.json"))[el.dataset.teardown]; } catch {}
    if (!t || !t.layers || !t.layers.length) { drop(el, el); return; }
    const n = t.layers.length, schem = !!t.schematic;
    el.style.setProperty("--n", n); el.style.setProperty("--mid", (n - 1) / 2);
    if (t.aspect) el.style.setProperty("--aspect", t.aspect);
    el.innerHTML = `<div class="td-pin"><div class="wrap td-grid">
      <div class="td-copy"><div class="td-top"><span class="eyebrow">${esc(t.eyebrow)}</span>${schem ? '<span class="td-schem">Schematic</span>' : ""}</div><h2>${escEm(t.title)}</h2>
        <ol class="td-list">${t.layers.map((l, i) => `<li><button data-i="${i}" aria-current="false"><span class="td-plus" aria-hidden="true">[+]</span><span class="td-n">${pad2(i)}</span><span class="td-name">${esc(l.name)}</span></button></li>`).join("")}</ol>
        <div class="td-detail" aria-live="polite"><p class="td-hint">Scroll to take it apart.</p></div></div>
      <div class="td-stage"><div class="td-stack">${t.layers.map((l, i) => `<div class="td-layer${l.img ? " img" : ""}" style="--i:${i}">
        ${l.img ? `<img src="${esc(l.img)}" alt="${esc(l.name)} module"${l.w ? ` width="${l.w}" height="${l.h}"` : ""} loading="lazy">` : blueprint(l.draw)}<span class="td-tag">${pad2(i)} · ${esc(l.name)}${schem ? " · schematic" : ""}</span></div>`).join("")}</div></div>
    </div></div>`;
    const stage = el.querySelector(".td-stage"), stack = el.querySelector(".td-stack"), layers = [...el.querySelectorAll(".td-layer")];
    const ol = el.querySelector(".td-list"), btns = [...ol.querySelectorAll("button")], detail = el.querySelector(".td-detail");
    // Under reduced motion the layers sit exploded from the start and only the active layer steps.
    const EXPLODE = reduce ? 0 : 0.16;
    let active = -2, near = false, queued = false, lastE = "", lastGap = -1, unsettle = 0;

    const show = i => {
      if (i === active) return; active = i;
      el.classList.toggle("stepping", i >= 0);
      // transform transitions only run while stepping (and briefly after), so the explode tracks scroll directly
      clearTimeout(unsettle);
      if (i >= 0) el.classList.add("settled"); else unsettle = setTimeout(() => el.classList.remove("settled"), 520);
      layers.forEach((l, k) => { l.classList.toggle("on", k === i); l.classList.toggle("above", k < i); });
      btns.forEach((b, k) => { b.setAttribute("aria-current", k === i); b.querySelector(".td-plus").textContent = k === i ? "[−]" : "[+]"; });
      if (i < 0) { detail.innerHTML = `<p class="td-hint">Scroll to take it apart.</p>`; return; }
      const l = t.layers[i];
      const link = l.link && !(l.link[0].startsWith("#") && !document.querySelector(l.link[0]));
      detail.innerHTML = `<span class="td-n">${pad2(i)} / ${pad2(n - 1)}</span><h3 class="td-h"></h3><p>${esc(l.body)}</p><span class="spec">${esc(l.spec)}</span>${
        link ? `<a class="td-link" href="${esc(l.link[0])}">${esc(l.link[1])} →</a>` : ""}`;
      scramble(detail.querySelector(".td-h"), l.head);
      scramble(btns[i].querySelector(".td-name"), l.name);
      // keep the active chip in view in the phone layout's scrollable row
      if (ol.scrollWidth > ol.clientWidth) ol.scrollLeft = btns[i].parentElement.offsetLeft - (ol.clientWidth - btns[i].parentElement.offsetWidth) / 2;
    };

    // Sizes are cached; frame() only reads the element rect and writes when a value changes.
    const measure = () => {
      // spread the layers to fill the stage height once tilted (rotateX 64deg: depth shows at ~0.9, a plate at ~0.44)
      const room = stage.offsetHeight * 0.9 - stack.offsetHeight * 0.44;
      const gap = Math.round(Math.max(24, Math.min(130, room / (0.9 * Math.max(1, n - 1)))));
      if (gap !== lastGap) { lastGap = gap; stack.style.setProperty("--gap", gap + "px"); }
    };
    const frame = () => {
      const r = el.getBoundingClientRect(), span = r.height - innerHeight;
      const p = span > 0 ? Math.min(1, Math.max(0, -r.top / span)) : 0;
      if (!reduce) {
        const e = Math.min(1, p / EXPLODE), ease = (1 - (1 - e) ** 3).toFixed(3);
        if (ease !== lastE) { lastE = ease; stack.style.setProperty("--e", ease); }
      }
      show(p < EXPLODE ? -1 : Math.min(n - 1, Math.floor((p - EXPLODE) / (1 - EXPLODE) * n)));
    };
    const tick = () => { if (!queued) { queued = true; requestAnimationFrame(() => { queued = false; frame(); }); } };
    addEventListener("scroll", () => { if (near) tick(); }, { passive: true });
    new IntersectionObserver(([en]) => { near = en.isIntersecting; el.classList.toggle("near", near); tick(); }, { rootMargin: "200px 0px" }).observe(el);
    new ResizeObserver(() => { measure(); tick(); }).observe(stage);
    addEventListener("resize", () => { measure(); tick(); });
    measure(); frame();
    btns.forEach((b, i) => b.addEventListener("click", () => {
      const span = el.offsetHeight - innerHeight, top = el.getBoundingClientRect().top + scrollY;
      scrollTo({ top: top + (EXPLODE + (i + 0.5) / n * (1 - EXPLODE)) * span, behavior: reduce ? "auto" : "smooth" });
    }));
  });

  // PARTS: every slot of the CUSTOM compressor and EQ, with the real part cards; pick parts to build one.
  // Slot strips and recipe buttons are never re-rendered on a pick, so keyboard focus stays where it is.
  document.querySelectorAll("[data-parts]").forEach(async el => {
    let data;
    try { data = await getJson("parts.json"); } catch { drop(el); return; }
    const keys = Object.keys(data);
    if (!keys.length) { drop(el); return; }
    const picks = Object.fromEntries(keys.map(k => [k, [...data[k].default]]));
    let cur = keys[0];
    el.innerHTML = `<div class="parts-bar"><div class="seg" role="group" aria-label="Part family">${keys.map((k, i) => `<button aria-pressed="${!i}" data-k="${k}">${esc(data[k].tab)}</button>`).join("")}</div>
      <p class="parts-count"></p></div><p class="parts-note"></p><p class="sr parts-status" role="status"></p><ol class="slots"></ol>
      <div class="build"><span class="eyebrow">Your build</span><div class="chips"></div><div class="recipes"></div></div>`;
    const list = el.querySelector(".slots"), build = el.querySelector(".build"), status = el.querySelector(".parts-status");
    const why = (k, s) => (data[k].unused || []).find(([slot, other, vals]) => slot === s && vals.includes(picks[k][other]))?.[3];
    const infoHtml = s => {
      const sl = data[cur].slots[s], o = sl.options[picks[cur][s]], off = why(cur, s);
      return `<span class="eyebrow">${esc(sl.name)} · ${sl.options.length} parts</span><b class="opt-name"></b>
          <p class="slot-guide">${esc(sl.guide)}</p><p>${esc(o.note)}</p>
          ${o.use ? `<p class="use"><span>Use on</span>${esc(o.use)}</p>` : ""}${o.bg ? `<p class="bg">${esc(o.bg)}</p>` : ""}
          ${off ? `<p class="why">${esc(off)}</p>` : ""}`;
    };
    const renderSlot = s => {
      const sl = data[cur].slots[s];
      list.children[s].innerHTML = `<span class="slot-n">${pad2(s)}</span><div class="slot-body">
        <figure class="slot-art"><img alt=""></figure><div class="slot-info"></div>
        <div class="slot-strip" role="group" aria-label="${esc(sl.name)} parts">${sl.options.map((p, i) =>
          `<button aria-pressed="false" data-o="${i}"><img src="${esc(p.img)}" alt=""${p.w ? ` width="${p.w}" height="${p.h}"` : ""} loading="lazy"><span>${esc(p.name)}</span></button>`).join("")}</div></div>`;
      updateSlot(s, false);
    };
    const updateSlot = (s, animate) => {
      const body = list.children[s].querySelector(".slot-body"), sl = data[cur].slots[s], pick = picks[cur][s], o = sl.options[pick];
      body.classList.toggle("off", !!why(cur, s));
      const img = body.querySelector(".slot-art img");
      if (img.getAttribute("src") !== o.img) img.src = o.img;
      img.alt = `${sl.name}: ${o.name} part`;
      body.querySelector(".slot-info").innerHTML = infoHtml(s);
      body.querySelectorAll(".slot-strip button").forEach((b, i) => b.setAttribute("aria-pressed", i === pick));
      const name = body.querySelector(".opt-name");
      animate ? scramble(name, o.name) : name.textContent = o.name;
    };
    const paintBuild = () => {
      const d = data[cur];
      el.querySelector(".chips").innerHTML = d.slots.map((sl, s) => `<span${why(cur, s) ? ' class="off"' : ""} title="${esc(sl.name)}">${esc(sl.options[picks[cur][s]].name)}</span>`).join("");
      el.querySelectorAll(".recipes button").forEach((b, i) => b.setAttribute("aria-pressed", d.recipes[i][1].every((x, s) => x === picks[cur][s])));
    };
    const paint = () => {
      const d = data[cur], total = d.slots.reduce((a, sl) => a + sl.options.length, 0);
      el.querySelector(".parts-count").innerHTML = `<b>${total}</b> parts in <b>${d.slots.length}</b> slots`;
      el.querySelector(".parts-note").textContent = d.note;
      list.innerHTML = d.slots.map(() => `<li class="slot"></li>`).join("");
      d.slots.forEach((_, s) => renderSlot(s));
      el.querySelector(".recipes").innerHTML = `<small>Recipes</small>` + d.recipes.map(([name], i) => `<button data-r="${i}" aria-pressed="false">${esc(name)}</button>`).join("");
      paintBuild();
    };
    el.querySelector(".parts-bar .seg").addEventListener("click", e => {
      const b = e.target.closest("button"); if (!b || b.dataset.k === cur) return;
      cur = b.dataset.k; el.querySelectorAll(".parts-bar .seg button").forEach(x => x.setAttribute("aria-pressed", x === b)); paint();
      status.textContent = `${data[cur].tab} parts`;
    });
    list.addEventListener("click", e => {
      const b = e.target.closest(".slot-strip button"); if (!b) return;
      const s = [...list.children].indexOf(b.closest(".slot"));
      const before = data[cur].slots.map((_, k) => why(cur, k));
      picks[cur][s] = +b.dataset.o;
      data[cur].slots.forEach((_, k) => k === s ? updateSlot(k, true) : why(cur, k) !== before[k] && updateSlot(k, false));
      paintBuild();
      status.textContent = `${data[cur].slots[s].name}: ${data[cur].slots[s].options[picks[cur][s]].name}`;
    });
    el.querySelector(".recipes").addEventListener("click", e => {
      const b = e.target.closest("button[data-r]"); if (!b) return;
      const rec = data[cur].recipes[+b.dataset.r];
      picks[cur] = [...rec[1]]; data[cur].slots.forEach((_, s) => updateSlot(s, true)); paintBuild();
      status.textContent = `Recipe: ${rec[0]}`;
    });
    paint();

    // The sticky build bar only pins once the first slot is clear of it, so it never covers that slot's strip.
    const wide = matchMedia("(min-width: 821px)");
    let onScreen = false, q = false;
    const pin = () => {
      q = false;
      const first = list.children[0]; if (!first) return;
      const clear = wide.matches && first.getBoundingClientRect().bottom < innerHeight - build.offsetHeight - 24;
      build.classList.toggle("pinned", clear);
    };
    const queuePin = () => { if (onScreen && !q) { q = true; requestAnimationFrame(pin); } };
    new IntersectionObserver(([en]) => { onScreen = en.isIntersecting; queuePin(); }, { rootMargin: "100px 0px" }).observe(el);
    addEventListener("scroll", queuePin, { passive: true }); addEventListener("resize", queuePin);
  });

  // Skin switchers: swap the image and rebuild its alt text from the original alt.
  document.querySelectorAll("[data-swap]").forEach(seg => {
    const img = document.getElementById(seg.dataset.swap); if (!img) return;
    const btns = [...seg.querySelectorAll("button")];
    seg.setAttribute("role", "group"); if (!seg.hasAttribute("aria-label")) seg.setAttribute("aria-label", "Skin");
    const alt0 = img.alt, start = btns.find(b => b.getAttribute("aria-pressed") === "true"), w0 = start ? start.textContent.trim() : "";
    const re = w0 && alt0.toLowerCase().includes(w0.toLowerCase()) ? new RegExp(escRe(w0), "i") : null;
    const altFor = b => b.dataset.alt || (re ? alt0.replace(re, () => b.textContent.trim()) : `${alt0.replace(/,?\s*\w+ skin$/i, "")}, ${b.textContent.trim()} skin`);
    btns.forEach(b => b.addEventListener("click", () => {
      btns.forEach(x => x.setAttribute("aria-pressed", x === b));
      img.src = b.dataset.src; img.alt = altFor(b);
    }));
  });
})();

// Walkthrough videos. Plays the local draft MP4; once data-youtube holds a video id, the same
// block loads the YouTube player instead (only after a click, so pages stay light).
// Draft: the local MP4s aren't published, so off localhost the walkthrough section
// shows only once every video in it has a YouTube id.
if (!/^(localhost|127\.0\.0\.1)$/.test(location.hostname)) {
  const sec = document.getElementById("walkthrough");
  if (sec && [...sec.querySelectorAll(".walk")].some(w => !w.dataset.youtube)) {
    sec.remove(); document.querySelectorAll('a[href="#walkthrough"]').forEach(a => a.remove());
  }
}
document.querySelectorAll(".walk").forEach(el => {
  const yt = el.dataset.youtube, poster = el.querySelector(".walk-play");
  let video = null;
  const start = (t = 0) => {
    if (yt) {
      const f = document.createElement("iframe");
      f.src = `https://www.youtube-nocookie.com/embed/${yt}?autoplay=1&start=${t}`;
      f.allow = "autoplay; encrypted-media; picture-in-picture"; f.allowFullscreen = true; f.title = poster.getAttribute("aria-label");
      el.querySelector("iframe, .walk-play").replaceWith(f); return;
    }
    if (!video) {
      video = document.createElement("video");
      video.src = el.dataset.src; video.controls = true; video.preload = "metadata";
      poster.replaceWith(video);
      const marks = [...el.querySelectorAll(".walk-ch button")];
      video.addEventListener("timeupdate", () => {
        let cur = 0; marks.forEach((b, i) => { if (video.currentTime >= +b.dataset.t) cur = i; });
        marks.forEach((b, i) => b.classList.toggle("on", i === cur));
      });
    }
    const go = () => { video.currentTime = t; video.play(); };
    video.readyState >= 1 ? go() : video.addEventListener("loadedmetadata", go, { once: true });
  };
  poster.addEventListener("click", () => start(0));
  el.querySelectorAll(".walk-ch button").forEach(b => b.addEventListener("click", () => start(+b.dataset.t)));
});
