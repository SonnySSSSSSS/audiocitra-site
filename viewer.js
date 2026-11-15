// Skin viewer and 3D gallery for the plug-in pages.
// <div data-viewer> holds <script type="application/json">{"name","mods":[{"name","title","text","skins":{"Skin":"img"}}]}</script>:
//   one frame, a module row (when there is more than one), a skin row, and Compare (drag between any two skins).
// <div data-gallery> holds tabs of <a href=big><img alt></a> thumbnails; a click opens a lightbox with arrows.
(() => {
  const el = (t, p = {}, kids = []) => { const e = Object.assign(document.createElement(t), p); e.append(...kids); return e; };
  const seg = (label, names, on) => {
    const s = el("div", { className: "seg" }); s.setAttribute("role", "group"); s.setAttribute("aria-label", label);
    names.forEach(n => { const b = el("button", { type: "button", textContent: n }); b.setAttribute("aria-pressed", n === on); b.dataset.v = n; s.append(b); });
    return s;
  };
  const press = (s, v) => s.querySelectorAll("button").forEach(b => b.setAttribute("aria-pressed", b.dataset.v === v));

  document.querySelectorAll("[data-viewer]").forEach(box => {
    const cfg = JSON.parse(box.querySelector("script").textContent), mods = cfg.mods;
    let m = mods[0], skin = Object.keys(m.skins)[0], vs = null;
    const a = el("img", { width: 1600, height: 900 }), b = el("img", { className: "top", width: 1600, height: 900 });
    const la = el("span", { className: "lbl l" }), lb = el("span", { className: "lbl r" });
    const range = el("input", { type: "range", min: 0, max: 100, value: 50 }); range.setAttribute("aria-label", "Compare skins");
    const frame = el("figure", { className: "plate vw-frame" }, [a, b, la, lb, el("div", { className: "bar" }), range]);
    range.addEventListener("input", () => frame.style.setProperty("--x", range.value + "%"));
    const modSeg = mods.length > 1 ? seg("Module", mods.map(x => x.name), m.name) : null;
    const skinSeg = seg("Skin", Object.keys(m.skins), skin);
    const cmp = el("button", { type: "button", className: "vw-cmp", textContent: "Compare" }); cmp.setAttribute("aria-pressed", "false");
    const vsSeg = seg("Compare with", Object.keys(m.skins), null);
    const vsRow = el("div", { className: "vw-row vw-vs", hidden: true }, [el("span", { className: "vw-k", textContent: "against" }), vsSeg]);
    const note = el("div", { className: "vw-note" });
    const alt = s => mods.length > 1 ? `${m.name} module, ${s} skin` : `${cfg.name} editor, ${s} skin`;
    const draw = () => {
      a.src = m.skins[skin]; a.alt = alt(skin);
      frame.classList.toggle("cmp", !!vs); vsRow.hidden = !vs;
      if (vs) { b.src = m.skins[vs]; b.alt = alt(vs); la.textContent = skin; lb.textContent = vs; }
      press(skinSeg, skin); press(vsSeg, vs);
      vsSeg.querySelectorAll("button").forEach(x => x.disabled = x.dataset.v === skin);
      note.innerHTML = m.title ? `<span class="eyebrow">${m.name}</span><h3>${m.title}</h3><p>${m.text}</p>` : "";
    };
    const other = () => Object.keys(m.skins).find(k => k !== skin);
    modSeg && modSeg.addEventListener("click", e => { const v = e.target.dataset && e.target.dataset.v; if (!v) return;
      m = mods.find(x => x.name === v); if (!m.skins[skin]) skin = Object.keys(m.skins)[0]; if (vs && (!m.skins[vs] || vs === skin)) vs = other(); press(modSeg, v); draw(); });
    skinSeg.addEventListener("click", e => { const v = e.target.dataset && e.target.dataset.v; if (!v) return; skin = v; if (vs === skin) vs = other(); draw(); });
    vsSeg.addEventListener("click", e => { const v = e.target.dataset && e.target.dataset.v; if (!v || v === skin) return; vs = v; draw(); });
    cmp.addEventListener("click", () => { vs = vs ? null : other(); cmp.setAttribute("aria-pressed", !!vs); draw(); });
    if (Object.keys(m.skins).length < 2) cmp.hidden = true;
    const rows = [];
    if (modSeg) rows.push(el("div", { className: "vw-row" }, [modSeg]));
    rows.push(el("div", { className: "vw-row" }, [skinSeg, cmp]), vsRow);
    box.append(frame, ...rows, note); draw();
  });

  // gallery: tabs over thumbnail grids, lightbox with arrows / swipe / Esc
  let lb, list = [], at = 0;
  const open = (items, i) => {
    if (!lb) {
      lb = el("dialog", { className: "lightbox" }, [el("img"), el("p"),
        el("button", { type: "button", className: "lb-x", textContent: "✕", ariaLabel: "Close" }),
        el("button", { type: "button", className: "lb-p", textContent: "←", ariaLabel: "Previous" }),
        el("button", { type: "button", className: "lb-n", textContent: "→", ariaLabel: "Next" })]);
      document.body.append(lb);
      lb.querySelector(".lb-x").onclick = () => lb.close();
      lb.querySelector(".lb-p").onclick = () => show(at - 1); lb.querySelector(".lb-n").onclick = () => show(at + 1);
      lb.addEventListener("click", e => { if (e.target === lb) lb.close(); });
      lb.addEventListener("keydown", e => { if (e.key === "ArrowLeft") show(at - 1); if (e.key === "ArrowRight") show(at + 1); });
      let x0 = null; lb.addEventListener("touchstart", e => { x0 = e.touches[0].clientX; }, { passive: true });
      lb.addEventListener("touchend", e => { if (x0 === null) return; const d = e.changedTouches[0].clientX - x0; if (Math.abs(d) > 40) show(at + (d < 0 ? 1 : -1)); x0 = null; });
    }
    list = items; show(i); lb.showModal();
  };
  const show = i => { at = (i + list.length) % list.length; const a = list[at], im = lb.querySelector("img");
    im.src = a.href; im.alt = a.querySelector("img").alt; const p = lb.querySelector("p"), pol = !!a.dataset.cap;
    lb.classList.toggle("pol", pol); p.style.top = ""; im.onload = null;
    if (pol) { p.innerHTML = ""; p.append(a.dataset.cap, Object.assign(document.createElement("span"), { textContent: ` · ${at + 1} / ${list.length}` }));
      const place = () => { const r = im.getBoundingClientRect(); p.style.top = (r.bottom - 52) + "px"; }; im.complete ? place() : im.onload = place; }
    else p.textContent = `${im.alt} · ${at + 1} / ${list.length}`; };
  document.querySelectorAll("[data-gallery]").forEach(g => {
    g.querySelectorAll(".gal-grid").forEach(grid => {
      const items = [...grid.querySelectorAll("a")];
      items.forEach((a, i) => a.addEventListener("click", e => { e.preventDefault(); open(items, i); }));
    });
  });
})();
