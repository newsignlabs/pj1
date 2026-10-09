/*
 * Collections page only — progressive enhancement.
 * Without this file every design is listed (thumbnails still lazy load) and a tap
 * opens the large photo directly.
 *  - "Show all" buttons: each category first shows a few designs; the hidden ones'
 *    thumbnails are not downloaded until revealed.
 *  - Viewer: tapping a design opens its large photo in a dialog. The large photo is
 *    fetched only then. Previous/next, arrow keys and swipe step through the category.
 */
(function () {
  "use strict";

  /* ---------- Show all designs in a category ---------- */
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

  /* ---------- Viewer ---------- */
  var viewer = document.querySelector("[data-viewer]");
  if (!viewer || typeof viewer.showModal !== "function") { return; }

  var root = document.documentElement;
  var img = viewer.querySelector(".viewer__img");
  var title = viewer.querySelector(".viewer__title");
  var count = viewer.querySelector("[data-count]");
  var links = [];
  var index = 0;

  var show = function (i) {
    index = (i + links.length) % links.length;
    var link = links[index];
    var thumb = link.querySelector("img");
    viewer.classList.add("is-loading");
    img.removeAttribute("src");
    img.alt = thumb.alt;
    img.src = link.getAttribute("href");
    title.textContent = link.querySelector("h3").textContent;
    count.textContent = (index + 1) + " / " + links.length;
  };

  img.addEventListener("load", function () { viewer.classList.remove("is-loading"); });
  img.addEventListener("error", function () { viewer.classList.remove("is-loading"); });

  document.addEventListener("click", function (event) {
    var link = event.target.closest("[data-zoom]");
    if (!link || event.ctrlKey || event.metaKey || event.shiftKey) { return; }
    event.preventDefault();
    links = Array.prototype.filter.call(link.closest(".piece-grid").querySelectorAll("[data-zoom]"), function (l) {
      return l.offsetParent !== null; /* skip designs still behind "Show all" */
    });
    show(links.indexOf(link));
    viewer.showModal();
    root.classList.add("menu-open"); /* lock page scroll */
  });

  viewer.addEventListener("close", function () {
    root.classList.remove("menu-open");
    img.removeAttribute("src");
    var link = links[index];
    if (link) { link.focus(); }
  });

  viewer.addEventListener("click", function (event) {
    if (event.target.closest("[data-close]") || event.target === viewer) {
      viewer.close();
      return;
    }
    var step = event.target.closest("[data-step]");
    if (step) { show(index + Number(step.getAttribute("data-step"))); }
  });

  viewer.addEventListener("keydown", function (event) {
    if (event.key === "ArrowLeft") { show(index - 1); }
    if (event.key === "ArrowRight") { show(index + 1); }
  });

  var startX = null;
  viewer.addEventListener("touchstart", function (event) {
    startX = event.touches.length === 1 ? event.touches[0].clientX : null;
  }, { passive: true });
  viewer.addEventListener("touchend", function (event) {
    if (startX === null) { return; }
    var dx = event.changedTouches[0].clientX - startX;
    if (Math.abs(dx) > 50) { show(index + (dx < 0 ? 1 : -1)); }
    startX = null;
  });
})();
