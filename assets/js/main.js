/*
 * Cute Look Bridal Jewels — progressive enhancement only.
 * The site works without this file: menu links show, the hero slider can be
 * swiped, quote backgrounds stay still, and the site stays in the dark theme.
 * The hero slider is the only thing that moves on its own (see its autoplay block).
 */
(function () {
  "use strict";

  /* ---------- Theme switch (dark default, light optional, remembered) ---------- */
  var root = document.documentElement;
  var themeSwitch = document.querySelector(".theme-switch");
  var themeMeta = document.querySelector('meta[name="theme-color"]');

  var applyTheme = function (theme) {
    var light = theme === "light";
    root.setAttribute("data-theme", light ? "light" : "dark");
    if (themeSwitch) {
      themeSwitch.setAttribute("aria-checked", String(light));
    }
    if (themeMeta) {
      themeMeta.setAttribute("content", light ? "#f7f2ec" : "#08070a");
    }
  };

  if (themeSwitch) {
    themeSwitch.hidden = false;
    applyTheme(root.getAttribute("data-theme"));
    themeSwitch.addEventListener("click", function () {
      var next = root.getAttribute("data-theme") === "light" ? "dark" : "light";
      applyTheme(next);
      try { localStorage.setItem("cutelook-theme", next); } catch (e) { /* private mode */ }
    });
  }

  /* ---------- Mobile navigation: full-screen menu ---------- */
  var header = document.querySelector(".site-header");
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("site-nav");

  if (header && toggle && nav) {
    var isOpen = function () { return header.classList.contains("is-open"); };

    var setOpen = function (open) {
      header.classList.toggle("is-open", open);
      root.classList.toggle("menu-open", open);
      toggle.setAttribute("aria-expanded", String(open));
      toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
      if (open) {
        var first = nav.querySelector("a");
        if (first) { first.focus(); }
      }
    };

    toggle.addEventListener("click", function () {
      setOpen(!isOpen());
    });

    document.addEventListener("keydown", function (event) {
      if (!isOpen()) { return; }
      if (event.key === "Escape") {
        setOpen(false);
        toggle.focus();
        return;
      }
      // Keep keyboard focus inside the open menu (toggle, theme switch and links).
      if (event.key === "Tab") {
        var items = [toggle].concat(Array.prototype.slice.call(nav.querySelectorAll("a")));
        if (themeSwitch && !themeSwitch.hidden) { items.push(themeSwitch); }
        items = items.filter(function (el) { return el.offsetParent !== null; });
        var i = items.indexOf(document.activeElement);
        var next = i === -1 ? 0 : (i + (event.shiftKey ? -1 : 1) + items.length) % items.length;
        event.preventDefault();
        items[next].focus();
      }
    });

    // Following a link (including same-page anchors) closes the menu.
    nav.addEventListener("click", function (event) {
      if (event.target.closest("a")) { setOpen(false); }
    });

    // The menu is phone-only: close it if the screen grows past the breakpoint.
    var wide = window.matchMedia("(min-width: 60rem)");
    var onWide = function () { if (wide.matches && isOpen()) { setOpen(false); } };
    if (wide.addEventListener) { wide.addEventListener("change", onWide); }
  }

  /* ---------- Footer year ---------- */
  var year = document.querySelector("[data-year]");
  if (year) {
    year.textContent = String(new Date().getFullYear());
  }

  /* ---------- Hero slider: auto-advances, with slide indicators, swipe and keyboard ---------- */
  var slider = document.querySelector("[data-slider]");
  if (slider) {
    var track = slider.querySelector(".hero__slides");
    var slides = track.querySelectorAll(".hero__slide");
    var dotsBox = slider.querySelector(".hero__dots");
    var dots = slider.querySelectorAll("[data-goto]");
    var status = slider.querySelector("[data-status]");
    var still = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var index = 0;

    var update = function () {
      for (var i = 0; i < slides.length; i++) {
        var hidden = i !== index;
        slides[i].inert = hidden;
        slides[i].setAttribute("aria-hidden", String(hidden));
      }
      for (var d = 0; d < dots.length; d++) {
        dots[d].classList.remove("is-active");
        dots[d].removeAttribute("aria-current");
      }
      if (dots[index]) {
        void dots[index].offsetWidth; // restart the progress fill
        dots[index].classList.add("is-active");
        dots[index].setAttribute("aria-current", "true");
      }
      status.textContent = "Slide " + (index + 1) + " of " + slides.length;
    };

    var go = function (i) {
      var wraps = i < 0 || i >= slides.length;
      index = (i + slides.length) % slides.length;
      // Slide smoothly between neighbours; jump when wrapping round or when motion is reduced.
      track.scrollTo({ left: index * track.clientWidth, behavior: still || wraps ? "instant" : "smooth" });
      update();
      schedule();
    };

    dotsBox.hidden = false;
    Array.prototype.forEach.call(dots, function (dot) {
      dot.addEventListener("click", function () { go(Number(dot.getAttribute("data-goto"))); });
    });

    track.addEventListener("keydown", function (event) {
      if (event.key === "ArrowLeft") { go(index - 1); }
      if (event.key === "ArrowRight") { go(index + 1); }
    });

    // Keep the progress bars in step with swipes (only once a scroll settles on a slide).
    track.addEventListener("scroll", function () {
      var pos = track.scrollLeft / track.clientWidth;
      var i = Math.round(pos);
      if (Math.abs(pos - i) < 0.02 && i !== index && i >= 0 && i < slides.length) {
        index = i;
        update();
        schedule();
      }
    }, { passive: true });

    // Stay on the same slide when the screen rotates or resizes.
    window.addEventListener("resize", function () {
      track.scrollTo({ left: index * track.clientWidth, behavior: "instant" });
    });

    /* autoplay-allowed:start — the site's only timer (constitution III). Auto-advance
       is off for prefers-reduced-motion, and pauses while the pointer or keyboard focus
       is in the hero, while it is touched, and when the tab is hidden. */
    var DELAY = 6000;
    var timer = null;
    var userPaused = still; // no auto-advance at all for reduced motion
    var held = false;

    function schedule() {
      clearTimeout(timer);
      slider.classList.toggle("is-paused", userPaused || held);
      if (!userPaused && !held && !document.hidden) {
        timer = setTimeout(function () { go(index + 1); }, DELAY);
      }
    }

    var hold = function (on) { held = on; schedule(); };
    slider.addEventListener("mouseenter", function () { hold(true); });
    slider.addEventListener("mouseleave", function () { hold(false); });
    slider.addEventListener("focusin", function () { hold(true); });
    slider.addEventListener("focusout", function (event) {
      if (!slider.contains(event.relatedTarget)) { hold(false); }
    });
    track.addEventListener("touchstart", function () { hold(true); }, { passive: true });
    track.addEventListener("touchend", function () { hold(false); }, { passive: true });
    document.addEventListener("visibilitychange", schedule);

    // Announce slide changes only when not auto-advancing (WAI carousel pattern).
    status.setAttribute("aria-live", userPaused ? "polite" : "off");
    /* autoplay-allowed:end */

    update();
    schedule();
  }

  /* ---------- Quote parallax fallback ----------
     Browsers with CSS scroll-driven animations do this in styles.css. Others
     (older Safari, Firefox) get the same effect here, driven only by scrolling. */
  var backgrounds = document.querySelectorAll(".quote__bg");
  var reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var cssDriven = window.CSS && CSS.supports && CSS.supports("animation-timeline: view()");

  if (backgrounds.length && !reduceMotion && !cssDriven) {
    var queued = false;
    var paint = function () {
      queued = false;
      var vh = window.innerHeight;
      for (var i = 0; i < backgrounds.length; i++) {
        var box = backgrounds[i].parentNode.getBoundingClientRect();
        if (box.bottom < 0 || box.top > vh) { continue; }
        var progress = (box.top + box.height) / (vh + box.height); // 1 entering, 0 leaving
        backgrounds[i].style.transform = "translate3d(0," + ((0.5 - progress) * 20).toFixed(2) + "%,0)";
      }
    };
    window.addEventListener("scroll", function () {
      if (!queued) {
        queued = true;
        window.requestAnimationFrame(paint);
      }
    }, { passive: true });
    paint();
  }
})();
