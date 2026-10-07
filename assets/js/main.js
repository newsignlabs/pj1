/*
 * Cute Look Bridal Jewels — progressive enhancement only.
 * The site works without this file: menu links show, the hero slider can be
 * swiped, quote backgrounds stay still, and the site stays in the dark theme.
 * Nothing here moves on its own: no timers, no autoplay.
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

  /* ---------- Hero slider: manual only (arrows, swipe, keyboard), instant ---------- */
  var slider = document.querySelector("[data-slider]");
  if (slider) {
    var track = slider.querySelector(".hero__slides");
    var slides = track.querySelectorAll(".hero__slide");
    var prev = slider.querySelector("[data-prev]");
    var next = slider.querySelector("[data-next]");
    var count = slider.querySelector(".hero__count");
    var current = slider.querySelector("[data-current]");
    var index = 0;

    var pad = function (n) { return (n < 10 ? "0" : "") + n; };

    var update = function () {
      current.textContent = pad(index + 1);
      for (var i = 0; i < slides.length; i++) {
        var hidden = i !== index;
        slides[i].inert = hidden;
        slides[i].setAttribute("aria-hidden", String(hidden));
      }
    };

    var go = function (i) {
      index = (i + slides.length) % slides.length;
      track.scrollTo({ left: index * track.clientWidth, behavior: "instant" });
      update();
    };

    prev.hidden = false;
    next.hidden = false;
    count.hidden = false;
    prev.addEventListener("click", function () { go(index - 1); });
    next.addEventListener("click", function () { go(index + 1); });

    track.addEventListener("keydown", function (event) {
      if (event.key === "ArrowLeft") { go(index - 1); }
      if (event.key === "ArrowRight") { go(index + 1); }
    });

    // Keep the counter in step with swipes.
    track.addEventListener("scroll", function () {
      var i = Math.round(track.scrollLeft / track.clientWidth);
      if (i !== index && i >= 0 && i < slides.length) {
        index = i;
        update();
      }
    }, { passive: true });

    // Stay on the same slide when the screen rotates or resizes.
    window.addEventListener("resize", function () {
      track.scrollTo({ left: index * track.clientWidth, behavior: "instant" });
    });

    update();
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
