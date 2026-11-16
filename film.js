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

// The rest of the site gets a lighter dose: a still-moving grain over the whole page, and on product pages the hero print
// gets its own dust and a soft vignette, as if the photo were sitting under a lamp. Nothing on top of text but the grain.
(() => {
  if (document.querySelector(".rooms")) return;
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const grain = document.createElement("div"); grain.className = "page-grain"; grain.setAttribute("aria-hidden", "true");
  document.body.append(grain);
  const print = document.querySelector(".plate.photo"); if (!print) return;
  const film = document.createElement("div"); film.className = "print-film"; film.setAttribute("aria-hidden", "true");
  film.innerHTML = '<div class="film-vig"></div><canvas class="film-dust"></canvas>';
  print.append(film);
  if (reduce) return;
  const cv = film.querySelector("canvas"), cx = cv.getContext("2d");
  let P = [], W = 0, H = 0, dpr = 1, on = false;
  function size() {
    dpr = Math.min(2, devicePixelRatio || 1); W = cv.width = film.clientWidth * dpr; H = cv.height = film.clientHeight * dpr;
    const n = innerWidth < 700 ? 10 : 24;
    while (P.length < n) P.push({ x: Math.random(), y: Math.random(), r: 0.6 + Math.random() ** 2 * 2.6, vx: (Math.random() - 0.5) * 3e-5,
      vy: -1.5e-5 - Math.random() * 4e-5, ph: Math.random() * 6.28, tw: 0.3 + Math.random() * 0.9, glint: 0 });
    P.length = n;
  }
  let last = performance.now();
  function frame(t) {
    if (!on) return;
    const dt = Math.min(50, t - last); last = t; cx.clearRect(0, 0, W, H);
    for (const p of P) {
      p.x += p.vx * dt + Math.sin(t / 3000 + p.ph) * 1.5e-5 * dt; p.y += p.vy * dt;
      if (p.y < -0.02) { p.y = 1.02; p.x = Math.random(); }
      if (p.x < -0.02) p.x = 1.02; else if (p.x > 1.02) p.x = -0.02;
      if (p.glint <= 0 && Math.random() < 3e-4 * dt / 16) p.glint = 1;
      p.glint = Math.max(0, p.glint - dt / 900);
      const a = Math.min(1, (0.14 + 0.18 * Math.sin(t / 1000 * p.tw + p.ph) ** 2) * 0.8 + p.glint * 0.35);
      const R = p.r * dpr * 2, X = p.x * W, Y = p.y * H, g = cx.createRadialGradient(X, Y, 0, X, Y, R);
      g.addColorStop(0, `rgba(255,244,222,${a})`); g.addColorStop(0.45, `rgba(255,244,222,${a * 0.35})`); g.addColorStop(1, "rgba(255,244,222,0)");
      cx.fillStyle = g; cx.beginPath(); cx.arc(X, Y, R, 0, 6.29); cx.fill();
    }
    requestAnimationFrame(frame);
  }
  // only animate while the print is on screen
  new IntersectionObserver(([e]) => { const was = on; on = e.isIntersecting; if (on && !was) { last = performance.now(); requestAnimationFrame(frame); } }).observe(print);
  addEventListener("resize", size); size();
})();
