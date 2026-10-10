/**
 * Real multi-layer parallax for homepage hero
 * Layers move at different speeds based on data-speed
 */
(function () {
  const hero = document.getElementById("hero-parallax");
  if (!hero) return;

  const layers = hero.querySelectorAll("[data-speed]");
  const prefersReduced =
    window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  if (prefersReduced || layers.length === 0) return;

  let ticking = false;

  function update() {
    const rect = hero.getBoundingClientRect();
    const heroH = hero.offsetHeight || 1;
    // progress: 0 at top of hero in view, increases as user scrolls down
    const scrolled = -rect.top;
    const progress = scrolled / heroH;

    layers.forEach(function (layer) {
      const speed = parseFloat(layer.getAttribute("data-speed")) || 0.5;
      // move downward slower than scroll → parallax depth
      const y = scrolled * (1 - speed);
      layer.style.transform = "translate3d(0, " + y.toFixed(2) + "px, 0)";
    });

    ticking = false;
  }

  function onScroll() {
    if (!ticking) {
      window.requestAnimationFrame(update);
      ticking = true;
    }
  }

  window.addEventListener("scroll", onScroll, { passive: true });
  window.addEventListener("resize", onScroll, { passive: true });
  update();
})();
