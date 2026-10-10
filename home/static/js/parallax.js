/**
 * Dramatic parallax:
 * - Background moves at ~20% of scroll speed (lags hard)
 * - Card moves at ~120% (slightly ahead) for depth contrast
 */
(function () {
  var hero = document.getElementById("px-hero");
  var bg = document.getElementById("px-bg");
  var card = document.getElementById("px-card");
  if (!hero || !bg) return;

  if (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    return;
  }

  var ticking = false;

  function frame() {
    var rect = hero.getBoundingClientRect();
    var heroTop = rect.top;
    var heroH = hero.offsetHeight || 1;

    // How far we've scrolled through the hero (px)
    // When hero top is at 0, scrolled = 0; as we scroll down, heroTop becomes negative
    var scrolled = -heroTop;

    // Only apply while hero is in/near viewport
    if (scrolled < -window.innerHeight || scrolled > heroH + window.innerHeight) {
      ticking = false;
      return;
    }

    // BG: moves SLOW — only 15–25% of scroll distance → obvious lag
    var bgY = scrolled * 0.35;
    bg.style.transform = "translate3d(0, " + bgY + "px, 0)";

    // Card: moves a bit FASTER than scroll for opposite depth
    if (card) {
      var cardY = scrolled * -0.18; // goes slightly up as you scroll down
      card.style.transform = "translate3d(0, " + cardY + "px, 0)";
    }

    ticking = false;
  }

  function onScroll() {
    if (!ticking) {
      requestAnimationFrame(frame);
      ticking = true;
    }
  }

  window.addEventListener("scroll", onScroll, { passive: true });
  window.addEventListener("resize", onScroll, { passive: true });
  frame();
})();
