/*
 * Collections page only — progressive enhancement.
 * Without this file every collection card is listed (thumbnails still lazy load) and a
 * tap opens the card's cover photo.
 *  - "Show all" buttons: each category first shows a few cards; the hidden cards'
 *    thumbnails are not downloaded until revealed.
 *  - Gallery: tapping a card (a sub-collection such as "Antique") opens a dialog with all
 *    of its photos. Photos are fetched only when shown (plus the next one, so stepping is
 *    quick). Previous/next buttons, thumbnails, arrow keys and swipe change the photo.
 */
(function () {
  "use strict";

  var PREFIX = "assets/img/pieces/";

  /* ---------- Show all cards in a category ---------- */
  Array.prototype.forEach.call(document.querySelectorAll("[data-more]"), function (button) {
    var grid = document.getElementById(button.getAttribute("aria-controls"));
    if (!grid) { return; }
    grid.classList.add("is-collapsed");
    button.hidden = false;
    button.addEventListener("click", function () {
      var first = grid.querySelector(".piece--more a");
      grid.classList.remove("is-collapsed");
      button.remove();
      if (first) { first.focus(); }
    });
  });

  /* ---------- Gallery ---------- */
  var viewer = document.querySelector("[data-viewer]");
  if (!viewer || typeof viewer.showModal !== "function") { return; }

  var root = document.documentElement;
  var img = viewer.querySelector(".viewer__img");
  var title = viewer.querySelector(".viewer__title");
  var count = viewer.querySelector("[data-count]");
  var thumbs = viewer.querySelector("[data-thumbs]");
  var steps = viewer.querySelectorAll("[data-step]");
  var opener = null;
  var photos = [];
  var name = "";
  var index = 0;

  var large = function (i) { return PREFIX + photos[i] + "-1080.webp"; };

  var show = function (i) {
    index = (i + photos.length) % photos.length;
    viewer.classList.add("is-loading");
    img.removeAttribute("src");
    img.alt = name + ", photo " + (index + 1) + " of " + photos.length;
    img.src = large(index);
    count.textContent = (index + 1) + " / " + photos.length;
    Array.prototype.forEach.call(thumbs.children, function (t, n) {
      t.setAttribute("aria-current", n === index ? "true" : "false");
    });
  };

  img.addEventListener("load", function () {
    viewer.classList.remove("is-loading");
    if (photos.length > 1) { new Image().src = large((index + 1) % photos.length); }
  });
  img.addEventListener("error", function () { viewer.classList.remove("is-loading"); });

  document.addEventListener("click", function (event) {
    var link = event.target.closest("[data-gallery]");
    if (!link || event.ctrlKey || event.metaKey || event.shiftKey) { return; }
    event.preventDefault();
    opener = link;
    photos = link.getAttribute("data-gallery").split("|");
    name = link.querySelector("h3").textContent;
    title.textContent = name;
    thumbs.textContent = "";
    if (photos.length > 1) {
      photos.forEach(function (p, n) {
        var b = document.createElement("button");
        var t = document.createElement("img");
        b.type = "button";
        b.className = "viewer__thumb";
        b.setAttribute("data-goto", n);
        b.setAttribute("aria-label", "Photo " + (n + 1));
        t.src = PREFIX + p + "-300.webp";
        t.alt = "";
        t.width = 60;
        t.height = 75;
        t.loading = "lazy";
        b.appendChild(t);
        thumbs.appendChild(b);
      });
    }
    Array.prototype.forEach.call(steps, function (s) { s.hidden = photos.length < 2; });
    show(0);
    viewer.showModal();
    root.classList.add("menu-open"); /* lock page scroll */
  });

  viewer.addEventListener("close", function () {
    root.classList.remove("menu-open");
    img.removeAttribute("src");
    if (opener) { opener.focus(); }
  });

  viewer.addEventListener("click", function (event) {
    if (event.target.closest("[data-close]") || event.target === viewer) {
      viewer.close();
      return;
    }
    var step = event.target.closest("[data-step]");
    if (step) { show(index + Number(step.getAttribute("data-step"))); }
    var go = event.target.closest("[data-goto]");
    if (go) { show(Number(go.getAttribute("data-goto"))); }
  });

  viewer.addEventListener("keydown", function (event) {
    if (event.key === "ArrowLeft") { show(index - 1); }
    if (event.key === "ArrowRight") { show(index + 1); }
  });

  var startX = null;
  viewer.addEventListener("touchstart", function (event) {
    var inStrip = event.target.closest("[data-thumbs]"); /* the strip scrolls sideways */
    startX = event.touches.length === 1 && !inStrip ? event.touches[0].clientX : null;
  }, { passive: true });
  viewer.addEventListener("touchend", function (event) {
    if (startX === null || photos.length < 2) { return; }
    var dx = event.changedTouches[0].clientX - startX;
    if (Math.abs(dx) > 50) { show(index + (dx < 0 ? 1 : -1)); }
    startX = null;
  });
})();
