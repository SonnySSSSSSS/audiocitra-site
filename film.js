// Film look for the homepage rooms (styles in site.css, "Film look"). Adds the per-room halation and tint, one overlay for the stage,
// and the dust: soft specks drifting on a canvas, the near ones out of focus, one now and then catching the light.
// The dust pauses with the tab (requestAnimationFrame) and is left out when the visitor asks for reduced motion.
(() => {
  const box = document.querySelector(".rooms"); if (!box) return;
  for (const r of box.querySelectorAll(".room")) {
    const img = r.querySelector(":scope > img"); if (!img) continue;
    const halo = img.cloneNode(); halo.className = "film-halo"; halo.alt = ""; halo.removeAttribute("id"); halo.setAttribute("aria-hidden", "true");
    const tint = document.createElement("div"); tint.className = "film-tint";
    img.after(halo, tint);
  }
  const film = document.createElement("div"); film.className = "film"; film.setAttribute("aria-hidden", "true");
  film.innerHTML = '<div class="film-lift"></div><div class="film-rays"></div><canvas class="film-dust"></canvas><div class="film-grain"></div><div class="film-flicker"></div><div class="film-vig"></div>';
  const bar = box.querySelector(".room-bar"); box.insertBefore(film, bar);
  if (matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  const cv = film.querySelector("canvas"), cx = cv.getContext("2d");
  let P = [], W = 0, H = 0, dpr = 1;
  function size() {
    dpr = Math.min(2, devicePixelRatio || 1); W = cv.width = film.clientWidth * dpr; H = cv.height = film.clientHeight * dpr;
    const n = Math.round((innerWidth < 700 ? 20 : 50) * Math.min(1, film.clientWidth * film.clientHeight / 1.2e6 + 0.4));
    while (P.length < n) P.push({ x: Math.random(), y: Math.random(), r: 0.6 + Math.random() ** 2 * 3.2, vx: (Math.random() - 0.5) * 4e-5,
      vy: -2e-5 - Math.random() * 6e-5, ph: Math.random() * 6.28, tw: 0.3 + Math.random() * 0.9, glint: 0 });
    P.length = n;
  }
  let last = performance.now();
  function frame(t) {
    const dt = Math.min(50, t - last); last = t; cx.clearRect(0, 0, W, H);
    for (const p of P) {
      p.x += p.vx * dt + Math.sin(t / 3000 + p.ph) * 2e-5 * dt; p.y += p.vy * dt;
      if (p.y < -0.02) { p.y = 1.02; p.x = Math.random(); }
      if (p.x < -0.02) p.x = 1.02; else if (p.x > 1.02) p.x = -0.02;
      if (p.glint <= 0 && Math.random() < 4e-4 * dt / 16) p.glint = 1;
      p.glint = Math.max(0, p.glint - dt / 900);
      const near = p.r > 2.6, a = Math.min(1, (0.18 + 0.22 * Math.sin(t / 1000 * p.tw + p.ph) ** 2) * 0.8 + p.glint * 0.4);
      const R = p.r * dpr * (near ? 1.8 : 1) * 2, X = p.x * W, Y = p.y * H;
      const g = cx.createRadialGradient(X, Y, 0, X, Y, R);
      g.addColorStop(0, `rgba(255,244,222,${a})`); g.addColorStop(near ? 0.25 : 0.45, `rgba(255,244,222,${a * 0.35})`); g.addColorStop(1, "rgba(255,244,222,0)");
      cx.fillStyle = g; cx.beginPath(); cx.arc(X, Y, R, 0, 6.29); cx.fill();
    }
    requestAnimationFrame(frame);
  }
  addEventListener("resize", size); size(); requestAnimationFrame(frame);
})();

// The rest of the site gets the same look as the homepage rooms. Every taped print gets the full stack (grade, halation, lifted blacks,
// grain, flicker, rays, vignette and dust), and the page itself gets grain, a soft vignette and dust drifting across the whole window.
(() => {
  if (document.querySelector(".rooms")) return;
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const page = document.createElement("div"); page.className = "page-film"; page.setAttribute("aria-hidden", "true");
  page.innerHTML = '<div class="film-grain"></div><div class="film-flicker"></div><div class="film-vig"></div><canvas class="film-dust"></canvas>';
  document.body.append(page);
  const layers = [{ host: page, cv: page.querySelector("canvas"), dense: 34, alwaysOn: true }];
  document.querySelectorAll(".plate.photo").forEach(print => {
    const img = print.querySelector("img");
    const film = document.createElement("div"); film.className = "print-film"; film.setAttribute("aria-hidden", "true");
    film.innerHTML = (img ? `<img class="film-halo" alt="" src="${img.currentSrc || img.src}">` : "") +
      '<div class="film-lift"></div><div class="film-rays"></div><canvas class="film-dust"></canvas><div class="film-grain"></div><div class="film-flicker"></div><div class="film-vig"></div>';
    print.append(film);
    layers.push({ host: film, cv: film.querySelector("canvas"), dense: 50, watch: print });
  });
  if (reduce) return;
  for (const L of layers) {
    L.cx = L.cv.getContext("2d"); L.P = []; L.on = !!L.alwaysOn;
    if (L.watch) new IntersectionObserver(([e]) => { L.on = e.isIntersecting; }).observe(L.watch);
  }
  function size() {
    const dpr = Math.min(2, devicePixelRatio || 1);
    for (const L of layers) {
      L.dpr = dpr; L.W = L.cv.width = L.host.clientWidth * dpr; L.H = L.cv.height = L.host.clientHeight * dpr;
      const n = Math.round((innerWidth < 700 ? L.dense * 0.4 : L.dense) * Math.min(1, L.host.clientWidth * L.host.clientHeight / 1.2e6 + 0.4));
      while (L.P.length < n) L.P.push({ x: Math.random(), y: Math.random(), r: 0.6 + Math.random() ** 2 * 3.2, vx: (Math.random() - 0.5) * 4e-5,
        vy: -2e-5 - Math.random() * 6e-5, ph: Math.random() * 6.28, tw: 0.3 + Math.random() * 0.9, glint: 0 });
      L.P.length = n;
    }
  }
  let last = performance.now();
  function frame(t) {
    const dt = Math.min(50, t - last); last = t;
    for (const L of layers) {
      if (!L.on) continue;
      const { cx, W, H, dpr } = L; cx.clearRect(0, 0, W, H);
      for (const p of L.P) {
        p.x += p.vx * dt + Math.sin(t / 3000 + p.ph) * 2e-5 * dt; p.y += p.vy * dt;
        if (p.y < -0.02) { p.y = 1.02; p.x = Math.random(); }
        if (p.x < -0.02) p.x = 1.02; else if (p.x > 1.02) p.x = -0.02;
        if (p.glint <= 0 && Math.random() < 4e-4 * dt / 16) p.glint = 1;
        p.glint = Math.max(0, p.glint - dt / 900);
        const near = p.r > 2.6, a = Math.min(1, (0.18 + 0.22 * Math.sin(t / 1000 * p.tw + p.ph) ** 2) * 0.8 + p.glint * 0.4);
        const R = p.r * dpr * (near ? 1.8 : 1) * 2, X = p.x * W, Y = p.y * H, g = cx.createRadialGradient(X, Y, 0, X, Y, R);
        g.addColorStop(0, `rgba(255,244,222,${a})`); g.addColorStop(near ? 0.25 : 0.45, `rgba(255,244,222,${a * 0.35})`); g.addColorStop(1, "rgba(255,244,222,0)");
        cx.fillStyle = g; cx.beginPath(); cx.arc(X, Y, R, 0, 6.29); cx.fill();
      }
    }
    requestAnimationFrame(frame);
  }
  addEventListener("resize", size); size(); requestAnimationFrame(frame);
})();
