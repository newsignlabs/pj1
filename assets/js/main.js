/*
 * Aurelia Bridal Jewels — progressive enhancement only.
 * The site works fully without this file: it adds the mobile menu toggle
 * and turns the contact form into a pre-filled WhatsApp message.
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

  /* ---------- Contact form -> WhatsApp ---------- */
  var form = document.getElementById("enquiry-form");
  if (!form) {
    return;
  }

  var number = form.getAttribute("data-wa-number");
  var dateInput = form.elements["wedding-date"];

  if (dateInput) {
    var today = new Date();
    var pad = function (n) { return (n < 10 ? "0" : "") + n; };
    dateInput.min = today.getFullYear() + "-" + pad(today.getMonth() + 1) + "-" + pad(today.getDate());
  }

  var formatDate = function (value) {
    var parts = value.split("-");
    if (parts.length !== 3) {
      return value;
    }
    var date = new Date(Number(parts[0]), Number(parts[1]) - 1, Number(parts[2]));
    return date.toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric" });
  };

  // "required" accepts whitespace-only input, so check trimmed values too.
  var requireText = function (field) {
    field.setCustomValidity(field.value.trim() ? "" : "Please fill in this field.");
  };

  ["name", "message"].forEach(function (name) {
    var field = form.elements[name];
    field.addEventListener("input", function () { requireText(field); });
  });

  form.addEventListener("submit", function (event) {
    event.preventDefault();

    var name = form.elements.name;
    var message = form.elements.message;
    requireText(name);
    requireText(message);
    if (!form.reportValidity()) {
      return;
    }

    var lines = ["Hello, I'm " + name.value.trim() + "."];
    var wedding = dateInput ? dateInput.value : "";
    var phone = form.elements.phone ? form.elements.phone.value.trim() : "";
    if (wedding) {
      lines.push("Wedding date: " + formatDate(wedding));
    }
    if (phone) {
      lines.push("Phone: " + phone);
    }
    lines.push("", message.value.trim());

    var url = "https://wa.me/" + number + "?text=" + encodeURIComponent(lines.join("\n"));
    var win = window.open(url, "_blank");
    if (win) {
      win.opener = null;
    } else {
      window.location.href = url; // pop-up blocked: open in the same tab
    }
  });
})();
