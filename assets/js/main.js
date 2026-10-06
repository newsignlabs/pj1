/*
 * Aurelia Bridal Jewels — progressive enhancement only.
 * The site works fully without this file: it adds the mobile menu toggle
 * and keeps the footer year current.
 */
(function () {
  "use strict";

  /* ---------- Mobile navigation ---------- */
  var header = document.querySelector(".site-header");
  var toggle = document.querySelector(".nav-toggle");

  if (header && toggle) {
    var setOpen = function (open) {
      header.classList.toggle("is-open", open);
      toggle.setAttribute("aria-expanded", String(open));
      toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    };

    toggle.addEventListener("click", function () {
      setOpen(!header.classList.contains("is-open"));
    });

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && header.classList.contains("is-open")) {
        setOpen(false);
        toggle.focus();
      }
    });

    document.addEventListener("click", function (event) {
      if (header.classList.contains("is-open") && !header.contains(event.target)) {
        setOpen(false);
      }
    });
  }

  /* ---------- Footer year ---------- */
  var year = document.querySelector("[data-year]");
  if (year) {
    year.textContent = String(new Date().getFullYear());
  }
})();
