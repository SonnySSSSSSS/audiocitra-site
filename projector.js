// Projector layout for product pages (body.projector; styles in site.css, "Projector").
// The page shows one stage: the hero beside its print, and a reel of slides, one per section. Picking a slide projects that
// section onto a screen over the dimmed page. The sections are the same elements as before, moved into the screen, so every
// player, plot and viewer keeps working. #listen etc. open the matching slide, and Back closes the screen.
(() => {
  if (!document.body.classList.contains("projector")) return;
  const main = document.querySelector("main"), stageWrap = main.querySelector(".wrap:has(>.hero)");
  if (!stageWrap) return;
  const secs = [...main.querySelectorAll(":scope > [id]")].filter(s => s.id && s !== stageWrap);
  if (!secs.length) return;
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const label = s => (s.querySelector(".eyebrow")?.firstChild?.textContent || s.id).trim();
  const title = s => s.querySelector("h2")?.innerHTML || "";
  const NAMES = { inside: "Take it apart", measurements: "Analysis", try: "Try it", features: "What's in it" };
  const items = secs.map((s, i) => ({ el: s, id: s.id, name: NAMES[s.id] || label(s), i }));
  stageWrap.classList.add("stage");

  // the reel
  const reel = document.createElement("nav"); reel.className = "reel"; reel.setAttribute("aria-label", "Sections");
  reel.innerHTML = `<div class="wrap"><ol>${items.map(it => `<li><a class="slide" href="#${it.id}" data-i="${it.i}">
    <span class="slide-n">${String(it.i + 1).padStart(2, "0")}</span><span class="slide-name">${it.name}</span></a></li>`).join("")}</ol></div>`;
  stageWrap.after(reel);

  // the screen
  const dlg = document.createElement("dialog"); dlg.className = "proj"; dlg.setAttribute("aria-labelledby", "proj-title");
  dlg.innerHTML = `<div class="proj-beam" aria-hidden="true"></div><div class="proj-screen">
    <header class="proj-bar"><span class="proj-n"></span><h2 id="proj-title" class="proj-title"></h2>
      <div class="proj-nav"><button type="button" class="proj-prev" aria-label="Previous section">←</button>
      <button type="button" class="proj-next" aria-label="Next section">→</button>
      <button type="button" class="proj-x" aria-label="Close" autofocus>✕</button></div></header>
    <div class="proj-body"></div><div class="proj-grain" aria-hidden="true"></div><div class="proj-flick" aria-hidden="true"></div></div>`;
  document.body.append(dlg);
  const body = dlg.querySelector(".proj-body"), nEl = dlg.querySelector(".proj-n"), tEl = dlg.querySelector(".proj-title");
  for (const it of items) { it.el.classList.add("proj-pane"); it.el.hidden = true; body.append(it.el); }

  let cur = -1, pushed = false;
  const quiet = pane => {
    pane.querySelectorAll("audio,video").forEach(a => a.pause());
    pane.querySelectorAll('.try-play[aria-pressed="true"]').forEach(b => b.click());
  };
  function show(i, { push = true } = {}) {
    i = (i + items.length) % items.length;
    if (cur >= 0 && cur !== i) { quiet(items[cur].el); items[cur].el.hidden = true; }
    const it = items[i]; it.el.hidden = false; cur = i;
    nEl.textContent = `${String(i + 1).padStart(2, "0")} / ${String(items.length).padStart(2, "0")}`;
    tEl.textContent = it.name;
    reel.querySelectorAll(".slide").forEach((a, k) => a.toggleAttribute("aria-current", k === i));
    if (!dlg.open) { dlg.showModal(); document.documentElement.classList.add("proj-open"); }
    dlg.scrollTop = 0; dlg.querySelector(".proj-screen").scrollTop = 0;
    body.scrollTop = 0;
    dlg.classList.remove("flash"); void dlg.offsetWidth; if (!reduce) dlg.classList.add("flash");
    if (push) { const url = "#" + it.id; if (pushed) history.replaceState({ proj: 1 }, "", url); else { history.pushState({ proj: 1 }, "", url); pushed = true; } }
    // panes were hidden while their scripts measured them; let them measure again now they can be seen
    requestAnimationFrame(() => dispatchEvent(new Event("resize")));
  }
  function close({ fromPop = false } = {}) {
    if (!dlg.open || document.querySelector("dialog[open]:not(.proj)")) return;
    if (cur >= 0) quiet(items[cur].el);
    dlg.close();
  }
  dlg.addEventListener("close", () => {
    document.documentElement.classList.remove("proj-open");
    const was = cur; cur = -1;
    if (was >= 0) items[was].el.hidden = true;  // else the next slide opens with this pane still showing above it
    reel.querySelectorAll(".slide").forEach(a => a.removeAttribute("aria-current"));
    if (pushed) { pushed = false; history.back(); }
    if (was >= 0) reel.querySelectorAll(".slide")[was]?.focus({ preventScroll: true });
  });
  addEventListener("popstate", () => {
    const k = items.findIndex(it => "#" + it.id === location.hash);
    if (k >= 0 && dlg.open) show(k, { push: false });
    else if (dlg.open) { pushed = false; dlg.close(); }
  });
  dlg.querySelector(".proj-x").addEventListener("click", () => close());
  dlg.querySelector(".proj-prev").addEventListener("click", () => show(cur - 1));
  dlg.querySelector(".proj-next").addEventListener("click", () => show(cur + 1));
  dlg.addEventListener("click", e => { if (e.target === dlg || e.target.classList.contains("proj-beam")) close(); });
  document.addEventListener("keydown", e => {
    if (!dlg.open || document.querySelector("dialog[open]:not(.proj)")) return;
    if (!e.target.closest || e.target.closest("input,select,textarea,[contenteditable]")) return;
    if (e.key === "ArrowRight" && !e.target.closest(".td-list,[data-viewer],.listen")) show(cur + 1);
    if (e.key === "ArrowLeft" && !e.target.closest(".td-list,[data-viewer],.listen")) show(cur - 1);
  });
  // a link to a section, or to something inside one (Akasa's analysis sits in Listen), opens that section's slide
  function paneOf(h) {
    if (!h || h.length < 2) return -1;
    let t; try { t = document.querySelector(h); } catch { return -1; }
    return t ? items.findIndex(it => it.el.contains(t)) : -1;
  }
  function reveal(h, k) {
    if (h === "#" + items[k].id) return;
    requestAnimationFrame(() => document.querySelector(h)?.scrollIntoView({ block: "start" }));
  }
  // any link on the page to a section opens its slide (hero buttons, the reel, teardown links)
  document.addEventListener("click", e => {
    const a = e.target.closest('a[href^="#"]'); if (!a) return;
    const h = a.getAttribute("href"), k = paneOf(h); if (k < 0) return;
    e.preventDefault(); show(k); reveal(h, k);
  });
  const h0 = location.hash, k0 = paneOf(h0);
  if (k0 >= 0) { history.replaceState(null, "", location.pathname + location.search); show(k0); reveal(h0, k0); }
})();
