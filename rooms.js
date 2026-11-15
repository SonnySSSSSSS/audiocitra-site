// Homepage rooms: one plug-in per screen, stepped sideways with arrows, keys, swipe or the strip.
// Without JS the rooms simply stack, so every plug-in stays reachable.
(() => {
  const box = document.querySelector(".rooms"); if (!box) return;
  const rooms = [...box.querySelectorAll(".room")], n = rooms.length;
  const bar = box.querySelector(".room-bar"), pos = box.querySelector(".room-pos"), strip = box.querySelector(".room-strip");
  const peek = box.querySelector(".room-peek");
  box.classList.add("js"); bar.hidden = false; peek.hidden = false;
  const name = r => r.getAttribute("aria-label");
  const tabs = rooms.map((r, k) => {
    const li = document.createElement("li"), b = document.createElement("button");
    b.type = "button"; b.textContent = name(r); b.style.setProperty("--c", r.style.getPropertyValue("--c"));
    b.addEventListener("click", () => show(k)); li.append(b); strip.append(li); return b;
  });
  let i = Math.max(0, rooms.findIndex(r => "#" + r.id === location.hash));
  function show(k, quiet) {
    i = (k + n) % n;
    rooms.forEach((r, j) => { const on = j === i; r.classList.toggle("on", on); r.inert = !on; r.setAttribute("aria-hidden", !on); });
    tabs.forEach((b, j) => b.setAttribute("aria-current", j === i));
    const r = rooms[i], nx = rooms[(i + 1) % n];
    box.style.setProperty("--c", r.style.getPropertyValue("--c"));
    pos.textContent = String(i).padStart(2, "0") + " / " + String(n - 1).padStart(2, "0");
    const pimg = nx.querySelector("img");
    peek.querySelector("img").src = pimg.currentSrc || pimg.src;
    peek.querySelector("span").textContent = name(nx);
    peek.style.setProperty("--pc", nx.style.getPropertyValue("--c"));
    peek.setAttribute("aria-label", "Next: " + name(nx));
    if (!quiet) history.replaceState(null, "", i ? "#" + r.id : location.pathname);
  }
  box.querySelector(".prev").addEventListener("click", () => show(i - 1));
  box.querySelector(".next").addEventListener("click", () => show(i + 1));
  peek.addEventListener("click", () => show(i + 1));
  // In-page links such as "Start with Spanda" point at a room.
  box.addEventListener("click", e => {
    const a = e.target.closest('a[href^="#"]'); if (!a) return;
    const k = rooms.findIndex(r => "#" + r.id === a.getAttribute("href")); if (k < 0) return;
    e.preventDefault(); show(k);
  });
  addEventListener("keydown", e => {
    if (e.altKey || e.ctrlKey || e.metaKey || /INPUT|TEXTAREA|SELECT/.test(document.activeElement?.tagName)) return;
    if (e.key === "ArrowRight") { show(i + 1); e.preventDefault(); }
    else if (e.key === "ArrowLeft") { show(i - 1); e.preventDefault(); }
  });
  let x0 = null, y0 = 0;
  box.addEventListener("touchstart", e => { x0 = e.touches[0].clientX; y0 = e.touches[0].clientY; }, { passive: true });
  box.addEventListener("touchend", e => {
    if (x0 == null) return; const t = e.changedTouches[0], dx = t.clientX - x0, dy = t.clientY - y0; x0 = null;
    if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy) * 1.5) show(i + (dx < 0 ? 1 : -1));
  }, { passive: true });
  addEventListener("hashchange", () => { const k = rooms.findIndex(r => "#" + r.id === location.hash); if (k >= 0) show(k, true); });
  show(i, true);
  requestAnimationFrame(() => requestAnimationFrame(() => box.classList.add("ready")));
})();
