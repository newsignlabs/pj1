/*
 * Cute Look photo admin.
 * Edits are collected locally (new photos, deletions, renames, category text) and saved
 * in one go: new photos are shrunk in the browser, uploaded to the gallery-api Catalyst
 * function, and committed to GitHub as a single commit. The GitHub workflow then builds
 * the site and Catalyst Slate publishes it.
 */
(function () {
  "use strict";

  var API = (window.CUTELOOK_ADMIN && window.CUTELOOK_ADMIN.api || "").replace(/\/+$/, "");
  var PIECES = "images-src/pieces/";
  var MAX_SIDE = 2400;
  var SEGMENT = /^[A-Za-z0-9][A-Za-z0-9 ._-]{0,79}$/;
  var SLOTS = [
    { label: "Slider · slide 1", folder: "images-src/hero/slide-1", thumb: "hero/hero-cinematic-540.webp" },
    { label: "Slider · slide 2", folder: "images-src/hero/slide-2", thumb: "hero/hero-detail-earrings-450.webp" },
    { label: "Slider · slide 3", folder: "images-src/hero/slide-3", thumb: "hero/hero-detail-pendant-450.webp" },
    { label: "Quote background", folder: "images-src/quotes/quote-chain", thumb: "quotes/quote-chain-600.webp" },
    { label: "“Some jewels are worn” card", folder: "images-src/features", thumb: "features/worn-temple-pendant-400.webp" },
    { label: "Our Story", folder: "images-src/about", thumb: "about/about-600.webp" },
    { label: "Logo (on black)", folder: "images-src/brand", thumb: "brand/logo-256.webp" }
  ];

  var $ = function (sel) { return document.querySelector(sel); };
  var el = function (tag, attrs, children) {
    var node = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) {
      if (k === "text") { node.textContent = attrs[k]; }
      else if (k.slice(0, 2) === "on") { node.addEventListener(k.slice(2), attrs[k]); }
      else if (attrs[k] !== false && attrs[k] != null) { node.setAttribute(k, attrs[k] === true ? "" : attrs[k]); }
    });
    (children || []).forEach(function (c) { if (c) { node.appendChild(typeof c === "string" ? document.createTextNode(c) : c); } });
    return node;
  };

  var session = null;
  try { session = JSON.parse(sessionStorage.getItem("cutelook-admin") || "null"); } catch (e) { /* private mode */ }
  var original = new Map();   // path -> sha (what is on GitHub now)
  var work = new Map();       // path -> {sha} | {file, url} ; + deleted flag
  var origCollections = { categories: [] };
  var collections = { categories: [] };
  var emptySubs = new Set();  // "category/sub" created here but still without photos
  var currentCat = null;
  var tab = "collections";
  var busy = false;

  /* ---------- Helpers ---------- */

  var slug = function (s) { return s.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "") || "photo"; };
  var natural = function (a, b) { return a.localeCompare(b, undefined, { numeric: true, sensitivity: "base" }); };
  var dir = function (p) { return p.slice(0, p.lastIndexOf("/")); };
  var base = function (p) { return p.slice(p.lastIndexOf("/") + 1); };
  var stem = function (name) { return name.replace(/\.[^.]+$/, ""); };
  // Same rule as tools/build_collections.py: "1-antique-premium" -> "Antique Premium"
  var titleFrom = function (name) {
    return name.replace(/^\d+[\s._-]+/, "").split(/[-_\s]+/).filter(Boolean).map(function (w) {
      return w === w.toUpperCase() ? w : w.charAt(0).toUpperCase() + w.slice(1);
    }).join(" ") || name;
  };

  function liveThumb(path) {
    if (path.indexOf(PIECES) !== 0) { return null; }
    var parts = path.slice(PIECES.length).split("/");
    var file = parts.pop();
    return "../assets/img/pieces/" + parts.map(slug).concat(slug(stem(file))).join("/") + "-300.webp";
  }

  function thumbFor(path) {
    var e = work.get(path);
    if (e.url) { return e.url; }
    if (original.get(path) === e.sha) { return liveThumb(path); }
    var from = null;
    original.forEach(function (sha, p) { if (!from && sha === e.sha) { from = p; } });
    return from ? liveThumb(from) : null;
  }

  function safeName(fileName, ext) {
    var s = stem(fileName).replace(/[^A-Za-z0-9 ._-]+/g, "-").replace(/^[^A-Za-z0-9]+/, "").slice(0, 60) || "photo";
    return s + ext;
  }

  function uniquePath(folder, name) {
    var path = folder + "/" + name, n = 2;
    while (work.has(path)) { path = folder + "/" + stem(name) + "-" + n + name.slice(stem(name).length); n += 1; }
    return path;
  }

  function sortPhotos(paths) {
    return paths.sort(function (a, b) {
      var ca = /^cover/i.test(base(a)), cb = /^cover/i.test(base(b));
      return ca === cb ? natural(stem(base(a)), stem(base(b))) : (ca ? -1 : 1);
    });
  }

  function banner(text, kind, link) {
    var b = $("#banner");
    b.hidden = !text;
    b.className = "banner" + (kind ? " is-" + kind : "");
    b.textContent = text || "";
    if (link) { b.appendChild(document.createTextNode(" ")); b.appendChild(el("a", { href: link, target: "_blank", rel: "noopener", text: "Details" })); }
  }

  /* ---------- API ---------- */

  function api(route, options) {
    options = options || {};
    if (!API) { return Promise.reject(new Error("The admin is not connected yet: set the function address in admin/config.js.")); }
    return fetch(API + "/" + route, {
      method: options.method || "GET",
      headers: Object.assign({ "Content-Type": "application/json" }, session ? { Authorization: "Bearer " + session.token } : {}),
      body: options.body ? JSON.stringify(options.body) : undefined
    }).then(function (res) {
      return res.json().catch(function () { return {}; }).then(function (data) {
        if (res.status === 401 && route !== "login") { logout(); }
        if (!res.ok) { throw new Error(data.error || ("Request failed (" + res.status + ").")); }
        return data;
      });
    });
  }

  /* ---------- Login ---------- */

  function showLogin() { $("#login-view").hidden = false; $("#app-view").hidden = true; }

  function logout() {
    session = null;
    try { sessionStorage.removeItem("cutelook-admin"); } catch (e) { /* ignore */ }
    showLogin();
  }

  $("#login-form").addEventListener("submit", function (event) {
    event.preventDefault();
    var form = event.target;
    $("#login-error").textContent = "";
    form.querySelector("button").disabled = true;
    api("login", { method: "POST", body: { username: form.username.value, password: form.password.value } })
      .then(function (data) {
        session = data;
        try { sessionStorage.setItem("cutelook-admin", JSON.stringify(data)); } catch (e) { /* ignore */ }
        form.password.value = "";
        start();
      })
      .catch(function (err) { $("#login-error").textContent = err.message; })
      .then(function () { form.querySelector("button").disabled = false; });
  });

  $("#logout").addEventListener("click", function () {
    if (pendingCount() && !confirm("You have unsaved changes. Log out anyway?")) { return; }
    logout();
  });

  /* ---------- Loading ---------- */

  function load() {
    return api("tree").then(function (data) {
      original = new Map();
      work.forEach(function (e) { if (e.url) { URL.revokeObjectURL(e.url); } });
      work = new Map();
      data.files.forEach(function (f) { original.set(f.path, f.sha); work.set(f.path, { sha: f.sha }); });
      origCollections = data.collections || { categories: [] };
      collections = JSON.parse(JSON.stringify(origCollections));
      emptySubs.clear();
      session.role = data.role;
      render();
    });
  }

  function start() {
    $("#login-view").hidden = true;
    $("#app-view").hidden = false;
    $("#user-name").textContent = session.name;
    $('[data-tab="pictures"]').hidden = session.role !== "developer";
    banner("Loading…");
    load().then(function () { banner(""); }).catch(function (err) { banner(err.message, "error"); });
  }

  /* ---------- Model queries ---------- */

  function categoryList() {
    var list = collections.categories.map(function (c) { return { id: c.id, folder: c.id, title: c.title }; });
    var known = new Set(list.map(function (c) { return c.folder; }));
    work.forEach(function (e, p) {
      if (p.indexOf(PIECES) !== 0) { return; }
      var folder = p.slice(PIECES.length).split("/")[0];
      if (!known.has(folder) && !e.deleted) { known.add(folder); list.push({ id: slug(folder), folder: folder, title: titleFrom(folder), extra: true }); }
    });
    return list;
  }

  function subsOf(folder) {
    var subs = new Map(), loose = [];
    work.forEach(function (e, p) {
      if (p.indexOf(PIECES + folder + "/") !== 0) { return; }
      var rest = p.slice((PIECES + folder + "/").length).split("/");
      if (rest.length === 2) {
        if (!subs.has(rest[0])) { subs.set(rest[0], []); }
        subs.get(rest[0]).push(p);
      } else if (rest.length === 1) { loose.push(p); }
    });
    emptySubs.forEach(function (key) {
      var i = key.indexOf("/");
      if (key.slice(0, i) === folder && !subs.has(key.slice(i + 1))) { subs.set(key.slice(i + 1), []); }
    });
    return { subs: Array.from(subs.keys()).sort(natural).map(function (name) { return { name: name, paths: sortPhotos(subs.get(name)) }; }), loose: sortPhotos(loose) };
  }

  function changes() {
    var list = [];
    work.forEach(function (e, p) {
      if (e.deleted) { if (original.has(p)) { list.push({ op: "delete", path: p }); } return; }
      if (e.file) { list.push({ op: "add", path: p, file: e.file }); }
      else if (original.get(p) !== e.sha) { list.push({ op: "add", path: p, sha: e.sha }); }
    });
    original.forEach(function (sha, p) { if (!work.has(p)) { list.push({ op: "delete", path: p }); } });
    return list;
  }

  var collectionsChanged = function () { return JSON.stringify(collections) !== JSON.stringify(origCollections); };
  var pendingCount = function () { return changes().length + (collectionsChanged() ? 1 : 0); };

  /* ---------- Editing ---------- */

  var pickTarget = null;
  function pickPhotos(folder, multiple) {
    var input = $("#file-input");
    pickTarget = folder;
    input.multiple = multiple !== false;
    input.value = "";
    input.click();
  }

  $("#file-input").addEventListener("change", function (event) {
    Array.prototype.forEach.call(event.target.files, function (file) {
      var path = uniquePath(pickTarget, safeName(file.name, ".jpg"));
      work.set(path, { file: file, url: URL.createObjectURL(file) });
    });
    emptySubs.delete(pickTarget.slice(PIECES.length));
    render();
  });

  function removePhoto(path) {
    var e = work.get(path);
    if (e.file) { URL.revokeObjectURL(e.url); work.delete(path); }
    else { e.deleted = !e.deleted; }
    render();
  }

  function move(from, to) {
    var e = work.get(from);
    work.delete(from);
    work.set(to, e);
  }

  function makeCover(path) {
    var folder = dir(path);
    work.forEach(function (e, p) {
      if (p !== path && dir(p) === folder && /^cover-/i.test(base(p))) { move(p, uniquePath(folder, base(p).replace(/^cover-/i, ""))); }
    });
    if (!/^cover/i.test(base(path))) { move(path, uniquePath(folder, "cover-" + base(path))); }
    render();
  }

  function askName(message, current) {
    var name = (prompt(message, current || "") || "").trim();
    if (!name) { return null; }
    if (!SEGMENT.test(name)) { alert("Use letters, numbers, spaces, dots, dashes or underscores (start with a letter or number)."); return null; }
    return name;
  }

  function renameSub(catFolder, sub) {
    var name = askName("New name for “" + titleFrom(sub) + "”:", titleFrom(sub));
    if (!name || name === sub) { return; }
    var from = PIECES + catFolder + "/" + sub + "/", to = PIECES + catFolder + "/" + name + "/";
    var clash = false;
    work.forEach(function (e, p) { if (p.indexOf(to) === 0) { clash = true; } });
    if (clash) { alert("“" + name + "” already exists in this category."); return; }
    Array.from(work.keys()).forEach(function (p) { if (p.indexOf(from) === 0) { move(p, to + p.slice(from.length)); } });
    if (emptySubs.delete(catFolder + "/" + sub)) { emptySubs.add(catFolder + "/" + name); }
    render();
  }

  function deleteFolder(prefix) {
    Array.from(work.keys()).forEach(function (p) {
      if (p.indexOf(prefix) !== 0) { return; }
      var e = work.get(p);
      if (e.file) { URL.revokeObjectURL(e.url); work.delete(p); } else { e.deleted = true; }
    });
  }

  /* ---------- Rendering ---------- */

  function photoTile(path, opts) {
    var e = work.get(path);
    var src = thumbFor(path);
    var wait = el("span", { class: "photo__wait", text: "Processing — appears after publishing", hidden: !!src });
    var img = src ? el("img", { src: src, alt: base(path), loading: "lazy", onerror: function () { img.hidden = true; wait.hidden = false; } }) : null;
    var tile = el("div", { class: "photo" + (e.deleted ? " is-deleted" : "") }, [
      img, wait,
      /^cover/i.test(base(path)) && !e.deleted ? el("span", { class: "photo__badge", text: "Cover" }) : null,
      e.file ? el("span", { class: "photo__badge photo__badge--new", text: "New" }) : null,
      el("div", { class: "photo__tools" }, [
        opts.cover && !e.deleted && !/^cover/i.test(base(path)) ? el("button", { type: "button", class: "icon-btn", title: "Make cover", "aria-label": "Make cover", text: "★", onclick: function () { makeCover(path); } }) : null,
        el("button", { type: "button", class: "icon-btn", title: e.deleted ? "Keep" : "Delete", "aria-label": e.deleted ? "Keep photo" : "Delete photo", text: e.deleted ? "↺" : "🗑", onclick: function () { removePhoto(path); } })
      ])
    ]);
    return tile;
  }

  function renderCategories() {
    var cats = categoryList();
    if (!cats.some(function (c) { return c.folder === currentCat; })) { currentCat = cats.length ? cats[0].folder : null; }
    var bar = $("#categories");
    bar.textContent = "";
    cats.forEach(function (c) {
      bar.appendChild(el("button", { type: "button", class: "chip", role: "tab", "aria-selected": String(c.folder === currentCat), text: c.title, onclick: function () { currentCat = c.folder; render(); } }));
    });
    if (session.role === "developer") {
      bar.appendChild(el("button", { type: "button", class: "chip", text: "+ Category", onclick: addCategory }));
    }
    return cats.filter(function (c) { return c.folder === currentCat; })[0];
  }

  function addCategory() {
    var title = (prompt("Name of the new category (e.g. Anklets):") || "").trim();
    if (!title) { return; }
    var id = slug(title);
    if (collections.categories.some(function (c) { return c.id === id; })) { alert("That category already exists."); return; }
    collections.categories.push({ id: id, title: title.slice(0, 60) });
    currentCat = id;
    render();
  }

  function renderCategory(cat) {
    var box = $("#category");
    box.textContent = "";
    if (!cat) { box.appendChild(el("p", { class: "muted", text: "No categories yet." })); return; }
    var entry = collections.categories.filter(function (c) { return c.id === cat.folder; })[0];

    var head = el("div", { class: "cat-head" });
    if (entry) {
      var title = el("input", { value: entry.title, maxlength: "60", oninput: function () { entry.title = title.value; updateTray(); } });
      var intro = el("textarea", { rows: "2", maxlength: "300", oninput: function () { entry.intro = intro.value; updateTray(); } });
      intro.value = entry.intro || "";
      head.appendChild(el("label", {}, ["Category title", title]));
      head.appendChild(el("label", {}, ["Short introduction (shown under the title)", intro]));
    } else {
      head.appendChild(el("p", { class: "muted", text: "This category comes from a folder only; it uses the folder name as its title." }));
    }
    var row = el("div", { class: "cat-head__row" }, [
      el("button", { type: "button", class: "btn", text: "+ New sub-collection", onclick: function () {
        var name = askName("Name of the new sub-collection (e.g. Antique Premium):");
        if (!name) { return; }
        emptySubs.add(cat.folder + "/" + name);
        render();
      } })
    ]);
    if (session.role === "developer") {
      row.appendChild(el("button", { type: "button", class: "btn btn--danger btn--small", text: "Delete category", onclick: function () {
        if (!confirm("Delete the whole “" + cat.title + "” category and all its photos?")) { return; }
        collections.categories = collections.categories.filter(function (c) { return c.id !== cat.folder; });
        deleteFolder(PIECES + cat.folder + "/");
        currentCat = null;
        render();
      } }));
    }
    head.appendChild(row);
    box.appendChild(head);

    var data = subsOf(cat.folder);
    if (!data.subs.length && !data.loose.length) {
      box.appendChild(el("p", { class: "muted", text: "No photos yet. Create a sub-collection and add photos to it." }));
    }
    data.subs.forEach(function (sub) {
      var folder = PIECES + cat.folder + "/" + sub.name;
      var live = sub.paths.filter(function (p) { return !work.get(p).deleted; }).length;
      var grid = el("div", { class: "photos" }, sub.paths.map(function (p) { return photoTile(p, { cover: true }); }).concat([
        el("button", { type: "button", class: "add-tile", onclick: function () { pickPhotos(folder); } }, [el("span", { text: "+" }), "Add photos"])
      ]));
      box.appendChild(el("article", { class: "sub" }, [
        el("div", { class: "sub__head" }, [
          el("h3", {}, [titleFrom(sub.name), el("small", { text: live + " photo" + (live === 1 ? "" : "s") })]),
          el("div", { class: "sub__actions" }, [
            el("button", { type: "button", class: "btn btn--small", text: "Rename", onclick: function () { renameSub(cat.folder, sub.name); } }),
            el("button", { type: "button", class: "btn btn--small btn--danger", text: "Delete", onclick: function () {
              if (!confirm("Delete “" + titleFrom(sub.name) + "” and its " + live + " photo(s)?")) { return; }
              deleteFolder(folder + "/");
              emptySubs.delete(cat.folder + "/" + sub.name);
              render();
            } })
          ])
        ]),
        grid
      ]));
    });
    if (data.loose.length) {
      box.appendChild(el("article", { class: "sub" }, [
        el("div", { class: "sub__head" }, [el("h3", { text: "Single photos" })]),
        el("div", { class: "photos" }, data.loose.map(function (p) { return photoTile(p, { cover: false }); }))
      ]));
    }
  }

  function renderSlots() {
    var box = $("#slots");
    box.textContent = "";
    var slots = SLOTS.slice();
    categoryList().forEach(function (c) {
      slots.push({ label: "Home card · " + c.title, folder: "images-src/collections/" + c.folder, thumb: "collections/" + c.folder + "-400.webp" });
    });
    slots.forEach(function (s) {
      var pending = null;
      work.forEach(function (e, p) { if (e.file && dir(p) === s.folder) { pending = p; } });
      var img = el("img", { src: pending ? work.get(pending).url : "../assets/img/" + s.thumb, alt: s.label, loading: "lazy" });
      box.appendChild(el("div", { class: "slot" }, [
        el("div", { class: "photo" }, [img, pending ? el("span", { class: "photo__badge photo__badge--new", text: "New" }) : null]),
        el("strong", { text: s.label }),
        pending
          ? el("button", { type: "button", class: "btn btn--small", text: "Undo", onclick: function () { removePhoto(pending); } })
          : el("button", { type: "button", class: "btn btn--small", text: "Replace photo", onclick: function () { pickPhotos(s.folder, false); } })
      ]));
    });
  }

  function updateTray() {
    var list = changes();
    var added = list.filter(function (c) { return c.op === "add" && c.file; }).length;
    var deleted = list.filter(function (c) { return c.op === "delete"; }).length;
    var moved = list.filter(function (c) { return c.op === "add" && c.sha; }).length;
    var parts = [];
    if (added) { parts.push(added + " new photo" + (added === 1 ? "" : "s")); }
    if (deleted - moved > 0) { parts.push((deleted - moved) + " deletion" + (deleted - moved === 1 ? "" : "s")); }
    if (moved) { parts.push(moved + " renamed or moved"); }
    if (collectionsChanged()) { parts.push("category details"); }
    $("#tray").hidden = !parts.length;
    $("#tray-text").textContent = "Unsaved: " + parts.join(", ");
    return parts.join(", ");
  }

  function render() {
    document.querySelectorAll(".tab").forEach(function (t) { t.setAttribute("aria-pressed", String(t.getAttribute("data-tab") === tab)); });
    $("#collections-panel").hidden = tab !== "collections";
    $("#pictures-panel").hidden = tab !== "pictures";
    if (tab === "collections") { renderCategory(renderCategories()); } else { renderSlots(); }
    updateTray();
  }

  document.querySelectorAll(".tab").forEach(function (t) {
    t.addEventListener("click", function () { tab = t.getAttribute("data-tab"); render(); });
  });

  $("#discard").addEventListener("click", function () {
    if (confirm("Discard all unsaved changes?")) { banner(""); load(); }
  });

  window.addEventListener("beforeunload", function (event) {
    if (session && pendingCount()) { event.preventDefault(); event.returnValue = ""; }
  });

  /* ---------- Saving ---------- */

  // Shrink to MAX_SIDE and re-encode as JPEG in the browser; keep the original if it cannot be decoded (e.g. HEIC on Chrome).
  function prepare(file) {
    return createImageBitmap(file, { imageOrientation: "from-image" }).then(function (bmp) {
      var scale = Math.min(1, MAX_SIDE / Math.max(bmp.width, bmp.height));
      var canvas = document.createElement("canvas");
      canvas.width = Math.round(bmp.width * scale);
      canvas.height = Math.round(bmp.height * scale);
      canvas.getContext("2d").drawImage(bmp, 0, 0, canvas.width, canvas.height);
      return new Promise(function (resolve) { canvas.toBlob(resolve, "image/jpeg", 0.88); });
    }).catch(function () {
      if (file.size > 10 * 1024 * 1024) { throw new Error(file.name + " is too large (over 10 MB)."); }
      return file;
    });
  }

  function toBase64(blob) {
    return new Promise(function (resolve, reject) {
      var reader = new FileReader();
      reader.onload = function () { resolve(String(reader.result).split(",")[1]); };
      reader.onerror = reject;
      reader.readAsDataURL(blob);
    });
  }

  $("#save").addEventListener("click", function () {
    if (busy) { return; }
    var list = changes();
    var summary = updateTray();
    busy = true;
    $("#save").disabled = $("#discard").disabled = true;
    var uploads = list.filter(function (c) { return c.file; });
    var done = 0;
    var chain = Promise.resolve();
    uploads.forEach(function (c) {
      chain = chain.then(function () {
        banner("Uploading photo " + (done + 1) + " of " + uploads.length + "…");
        return prepare(c.file).then(toBase64).then(function (content) {
          return api("blob", { method: "POST", body: { content: content } });
        }).then(function (res) { c.sha = res.sha; done += 1; });
      });
    });
    chain.then(function () {
      banner("Saving…");
      return api("commit", { method: "POST", body: {
        message: summary,
        changes: list.map(function (c) { return { op: c.op, path: c.path, sha: c.sha }; }),
        collections: collectionsChanged() ? collections : undefined
      } });
    }).then(function (res) {
      banner("Saved. Publishing to the website… (usually 2–3 minutes)");
      watch(res.commit, 0);
      return load();
    }).catch(function (err) {
      banner(err.message, "error");
    }).then(function () {
      busy = false;
      $("#save").disabled = $("#discard").disabled = false;
    });
  });

  function watch(sha, tries) {
    setTimeout(function () {
      api("status?sha=" + sha).then(function (s) {
        if (s.state !== "completed") {
          if (tries < 60) { watch(sha, tries + 1); }
          return;
        }
        if (s.conclusion === "success") { banner("Published ✓  The website shows the changes within a minute.", "ok"); }
        else { banner("Publishing failed. The developer has been shown the details.", "error", s.url); }
      }).catch(function () { if (tries < 60) { watch(sha, tries + 1); } });
    }, 10000);
  }

  /* ---------- Start ---------- */

  if (session && session.token) { start(); } else { showLogin(); }
})();
