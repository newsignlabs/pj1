/*
 * gallery-api — Catalyst Advanced I/O function behind the Cute Look admin page (/admin/).
 *
 * It holds the GitHub App key, checks the admin's login and commits photo changes to the
 * repository. The "Build site from photo folders" workflow then builds the pictures and
 * Catalyst Slate publishes the site. No npm dependencies (Node 18+).
 *
 * Routes (JSON; all but /login need "Authorization: Bearer <token>"):
 *   POST /login   {username, password}            -> {token, name, role}
 *   GET  /tree                                    -> {head, role, files[], collections}
 *   POST /blob    {content: base64 image}         -> {sha}
 *   POST /commit  {message, changes[], collections?} -> {commit}
 *   GET  /status?sha=<commit>                     -> {state, conclusion, url}
 *
 * Roles: "client" manages Collections photos and sub-collections and edits category titles
 * and intros; "developer" can also add or remove categories and replace the slider, quote,
 * category-card, feature, Our Story and logo pictures.
 *
 * Environment variables (Catalyst console > Functions > gallery-api > Configuration):
 *   GH_APP_ID, GH_INSTALLATION_ID, GH_PRIVATE_KEY   GitHub App (private key PEM; "\n" allowed)
 *   GH_OWNER, GH_REPO, GH_BRANCH                    e.g. newsignlabs, pj1, main
 *   DEVELOPER_PASSWORD, CLIENT_PASSWORD   the two admin passwords (plain text)
 *   DEVELOPER_USERNAME, CLIENT_USERNAME   optional; default "developer" and "cutelook"
 *   SESSION_SECRET  long random string (signs login sessions)
 *   ALLOWED_ORIGINS comma-separated site origins, e.g. https://pj1-midrqtyj.onslate.in
 */
"use strict";

const crypto = require("crypto");

const env = (name, fallback) => {
  const value = process.env[name];
  if (value === undefined || value === "") {
    if (fallback !== undefined) return fallback;
    throw new HttpError(500, `Server is not configured (${name} missing).`);
  }
  return value;
};

class HttpError extends Error {
  constructor(status, message) {
    super(message);
    this.status = status;
  }
}

/* ---------- Login sessions ---------- */

const SESSION_HOURS = 12;

function b64url(buf) {
  return Buffer.from(buf).toString("base64").replace(/=+$/, "").replace(/\+/g, "-").replace(/\//g, "_");
}

function sign(payload) {
  const body = b64url(JSON.stringify(payload));
  const mac = b64url(crypto.createHmac("sha256", env("SESSION_SECRET")).update(body).digest());
  return `${body}.${mac}`;
}

function verify(token) {
  const [body, mac] = String(token || "").split(".");
  if (!body || !mac) return null;
  const expected = b64url(crypto.createHmac("sha256", env("SESSION_SECRET")).update(body).digest());
  if (mac.length !== expected.length || !crypto.timingSafeEqual(Buffer.from(mac), Buffer.from(expected))) return null;
  try {
    const payload = JSON.parse(Buffer.from(body.replace(/-/g, "+").replace(/_/g, "/"), "base64").toString());
    return payload.exp > Date.now() ? payload : null;
  } catch (e) {
    return null;
  }
}

// The two admin accounts, from plain-text passwords in the function's environment variables.
function users() {
  const list = [
    { username: env("DEVELOPER_USERNAME", "developer"), name: "Developer", role: "developer", password: process.env.DEVELOPER_PASSWORD },
    { username: env("CLIENT_USERNAME", "cutelook"), name: "Cute Look", role: "client", password: process.env.CLIENT_PASSWORD },
  ].filter((u) => u.password);
  if (!list.length) throw new HttpError(500, "Server is not configured (DEVELOPER_PASSWORD / CLIENT_PASSWORD missing).");
  return list.map((u) => ({ ...u, username: u.username.trim().toLowerCase() }));
}

// Compare fixed-length digests so the check takes the same time whatever is typed.
const digest = (text) => crypto.createHash("sha256").update(String(text)).digest();

async function login(body) {
  const typed = digest(body.password || "");
  const user = users().find((u) => u.username === String(body.username || "").trim().toLowerCase());
  const ok = user && crypto.timingSafeEqual(typed, digest(user.password));
  if (!ok) {
    await new Promise((r) => setTimeout(r, 600)); // slow down guessing
    throw new HttpError(401, "Wrong username or password.");
  }
  const token = sign({ u: user.username, name: user.name, role: user.role, exp: Date.now() + SESSION_HOURS * 3600e3 });
  return { token, name: user.name, role: user.role };
}

/* ---------- GitHub App ---------- */

let cachedToken = null;

// Accept the private key however it was pasted: with real line breaks, with "\n", with the
// line breaks turned into spaces (common when pasting into a one-line field on a phone), or
// even without the -----BEGIN/END----- lines.
function pem(raw) {
  const text = String(raw).replace(/\\n/g, "\n").trim();
  const m = text.match(/-----BEGIN ([A-Z ]+)-----([\s\S]*?)-----END \1-----/);
  const body = (m ? m[2] : text.replace(/-----[A-Z ]+-----/g, "")).replace(/\s+/g, "");
  if (!/^MII[A-Za-z0-9+/=]+$/.test(body)) throw new HttpError(500, "GH_PRIVATE_KEY is not a private key.");
  // GitHub App keys are PKCS#1 ("RSA PRIVATE KEY"); PKCS#8 keys carry the RSA algorithm id.
  const label = m ? m[1] : /^MII.{0,8}IBADANBgkqhkiG9w0BAQEF/.test(body) ? "PRIVATE KEY" : "RSA PRIVATE KEY";
  return `-----BEGIN ${label}-----\n${body.match(/.{1,64}/g).join("\n")}\n-----END ${label}-----\n`;
}

async function installationToken() {
  if (cachedToken && cachedToken.expires - Date.now() > 5 * 60e3) return cachedToken.token;
  const now = Math.floor(Date.now() / 1000);
  const head = b64url(JSON.stringify({ alg: "RS256", typ: "JWT" }));
  const claims = b64url(JSON.stringify({ iat: now - 60, exp: now + 540, iss: env("GH_APP_ID") }));
  const key = pem(env("GH_PRIVATE_KEY"));
  const signature = b64url(crypto.createSign("RSA-SHA256").update(`${head}.${claims}`).sign(key));
  const res = await gh(`/app/installations/${env("GH_INSTALLATION_ID")}/access_tokens`, {
    method: "POST",
    auth: `Bearer ${head}.${claims}.${signature}`,
  });
  cachedToken = { token: res.token, expires: Date.parse(res.expires_at) };
  return res.token;
}

async function gh(path, { method = "GET", body, auth } = {}) {
  const base = env("GH_API_URL", "https://api.github.com");
  const res = await fetch(base + path, {
    method,
    headers: {
      Accept: "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
      "User-Agent": "cutelook-gallery-api",
      Authorization: auth || `Bearer ${await installationToken()}`,
      ...(body ? { "Content-Type": "application/json" } : {}),
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  const text = await res.text();
  const data = text ? JSON.parse(text) : {};
  if (!res.ok) {
    const err = new HttpError(res.status === 409 || res.status === 422 ? 409 : 502, `GitHub: ${data.message || res.status}`);
    err.github = res.status;
    throw err;
  }
  return data;
}

const repo = () => `/repos/${env("GH_OWNER")}/${env("GH_REPO")}`;
const branch = () => env("GH_BRANCH", "main");

async function headCommit() {
  const ref = await gh(`${repo()}/git/ref/heads/${branch()}`);
  const commit = await gh(`${repo()}/git/commits/${ref.object.sha}`);
  return { sha: ref.object.sha, tree: commit.tree.sha };
}

/* ---------- Allowed paths ---------- */

const IMAGE = /\.(jpe?g|png|webp|heic|heif)$/i;
const SEGMENT = /^[A-Za-z0-9][A-Za-z0-9 ._-]{0,79}$/;
const COLLECTIONS_JSON = "content/collections.json";

function segmentsOk(parts) {
  return parts.every((p) => SEGMENT.test(p) && !p.includes(".."));
}

// Photos a role may add or delete.
function photoAllowed(path, role) {
  const parts = path.split("/");
  if (!segmentsOk(parts) || !IMAGE.test(path)) return false;
  // images-src/pieces/<category>/<sub-collection>/<photo>
  if (parts[0] === "images-src" && parts[1] === "pieces" && parts.length === 5) return true;
  if (role !== "developer" || parts[0] !== "images-src") return false;
  const slot = parts.slice(1, -1).join("/");
  return (
    (parts[1] === "pieces" && parts.length === 4) || // loose photo in a category
    /^hero\/slide-[1-3]$/.test(slot) ||
    slot === "quotes/quote-chain" ||
    (parts[1] === "collections" && parts.length === 4) ||
    ["about", "features", "brand"].includes(slot)
  );
}

function validateCollections(next, current, role) {
  if (!next || !Array.isArray(next.categories)) throw new HttpError(400, "Categories are missing.");
  const ids = new Set();
  const categories = next.categories.map((c) => {
    const id = String(c.id || "");
    if (!/^[a-z0-9]+(-[a-z0-9]+)*$/.test(id) || ids.has(id)) throw new HttpError(400, `Bad category id "${id}".`);
    ids.add(id);
    const title = String(c.title || "").trim();
    if (!title || title.length > 60) throw new HttpError(400, `Category "${id}" needs a title (up to 60 characters).`);
    const out = { id, title };
    const intro = String(c.intro || "").trim();
    if (intro.length > 300) throw new HttpError(400, `Intro for "${title}" is too long.`);
    if (intro) out.intro = intro;
    return out;
  });
  if (role !== "developer") {
    const before = (current.categories || []).map((c) => c.id).sort().join(",");
    if ([...ids].sort().join(",") !== before) throw new HttpError(403, "Only the developer account can add or remove categories.");
  }
  return { ...(current._help ? { _help: current._help } : {}), categories };
}

/* ---------- Routes ---------- */

async function readTree() {
  const head = await headCommit();
  const tree = await gh(`${repo()}/git/trees/${head.tree}?recursive=1`);
  const files = tree.tree
    .filter((t) => t.type === "blob" && t.path.startsWith("images-src/") && IMAGE.test(t.path))
    .map((t) => ({ path: t.path, sha: t.sha, size: t.size }));
  const entry = tree.tree.find((t) => t.path === COLLECTIONS_JSON);
  let collections = { categories: [] };
  if (entry) {
    const blob = await gh(`${repo()}/git/blobs/${entry.sha}`);
    collections = JSON.parse(Buffer.from(blob.content, "base64").toString("utf8"));
  }
  return { head: head.sha, files, collections, paths: new Set(tree.tree.map((t) => t.path)) };
}

function looksLikeImage(buf) {
  const hex = buf.subarray(0, 12).toString("hex");
  return (
    hex.startsWith("ffd8ff") || // JPEG
    hex.startsWith("89504e47") || // PNG
    (hex.startsWith("52494646") && buf.subarray(8, 12).toString() === "WEBP") ||
    buf.subarray(4, 8).toString() === "ftyp" // HEIC / HEIF
  );
}

async function createBlob(body) {
  const content = String(body.content || "");
  const bytes = Buffer.from(content, "base64");
  if (!bytes.length || bytes.length > 12 * 1024 * 1024) throw new HttpError(413, "Photo is empty or larger than 12 MB.");
  if (!looksLikeImage(bytes)) throw new HttpError(415, "Only JPG, PNG, WebP or HEIC photos can be uploaded.");
  const blob = await gh(`${repo()}/git/blobs`, { method: "POST", body: { content, encoding: "base64" } });
  return { sha: blob.sha };
}

async function commit(body, session) {
  const changes = Array.isArray(body.changes) ? body.changes : [];
  if (!changes.length && !body.collections) throw new HttpError(400, "Nothing to save.");
  if (changes.length > 200) throw new HttpError(400, "Too many changes at once (200 max).");

  for (let attempt = 0; attempt < 3; attempt += 1) {
    const current = await readTree();
    const entries = [];
    const touched = new Set();
    for (const c of changes) {
      const path = String(c.path || "");
      if (touched.has(path)) throw new HttpError(400, `"${path}" is changed twice.`);
      touched.add(path);
      if (!photoAllowed(path, session.role)) throw new HttpError(403, `Not allowed: ${path}`);
      if (c.op === "add") {
        if (!/^[0-9a-f]{40}$/.test(String(c.sha))) throw new HttpError(400, "Bad photo reference.");
        entries.push({ path, mode: "100644", type: "blob", sha: c.sha });
      } else if (c.op === "delete") {
        if (!current.paths.has(path)) continue; // already gone
        entries.push({ path, mode: "100644", type: "blob", sha: null });
      } else {
        throw new HttpError(400, "Unknown change.");
      }
    }
    if (body.collections) {
      const json = validateCollections(body.collections, current.collections, session.role);
      const blob = await gh(`${repo()}/git/blobs`, {
        method: "POST",
        body: { content: JSON.stringify(json, null, 2) + "\n", encoding: "utf-8" },
      });
      entries.push({ path: COLLECTIONS_JSON, mode: "100644", type: "blob", sha: blob.sha });
    }
    if (!entries.length) throw new HttpError(400, "Nothing to save.");

    const base = await gh(`${repo()}/git/commits/${current.head}`);
    const tree = await gh(`${repo()}/git/trees`, { method: "POST", body: { base_tree: base.tree.sha, tree: entries } });
    const summary = String(body.message || "Update photos").replace(/\s+/g, " ").slice(0, 120);
    const made = await gh(`${repo()}/git/commits`, {
      method: "POST",
      body: { message: `Admin (${session.name}): ${summary}`, tree: tree.sha, parents: [current.head] },
    });
    try {
      await gh(`${repo()}/git/refs/heads/${branch()}`, { method: "PATCH", body: { sha: made.sha, force: false } });
      return { commit: made.sha };
    } catch (err) {
      if (err.github !== 422 || attempt === 2) throw err; // main moved meanwhile: rebuild on the new head
    }
  }
  throw new HttpError(409, "The site changed while saving. Please try again.");
}

async function status(sha) {
  if (!/^[0-9a-f]{40}$/.test(String(sha))) throw new HttpError(400, "Bad commit.");
  const runs = await gh(`${repo()}/actions/runs?head_sha=${sha}&per_page=5`);
  const run = (runs.workflow_runs || [])[0];
  if (!run) return { state: "queued" };
  return { state: run.status, conclusion: run.conclusion, url: run.html_url };
}

/* ---------- HTTP plumbing ---------- */

function readBody(req, limit = 17 * 1024 * 1024) {
  return new Promise((resolve, reject) => {
    if (req.body !== undefined && typeof req.body === "object" && !Buffer.isBuffer(req.body)) return resolve(req.body);
    let size = 0;
    const chunks = [];
    req.on("data", (c) => {
      size += c.length;
      if (size > limit) {
        reject(new HttpError(413, "Request too large."));
        req.destroy();
      } else chunks.push(c);
    });
    req.on("end", () => {
      try {
        resolve(chunks.length ? JSON.parse(Buffer.concat(chunks).toString("utf8")) : {});
      } catch (e) {
        reject(new HttpError(400, "Invalid JSON."));
      }
    });
    req.on("error", reject);
  });
}

function send(res, status, data, origin) {
  const headers = { "Content-Type": "application/json", "Cache-Control": "no-store" };
  if (origin) {
    headers["Access-Control-Allow-Origin"] = origin;
    headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type";
    headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS";
    headers.Vary = "Origin";
  }
  res.writeHead(status, headers);
  res.end(JSON.stringify(data));
}

module.exports = async (req, res) => {
  const allowed = String(process.env.ALLOWED_ORIGINS || "").split(",").map((s) => s.trim()).filter(Boolean);
  const origin = allowed.includes(req.headers.origin) ? req.headers.origin : "";
  try {
    if (req.method === "OPTIONS") return send(res, 204, {}, origin);
    const url = new URL(req.url, "http://local");
    const route = url.pathname.replace(/\/+$/, "").split("/").pop();

    if (route === "login" && req.method === "POST") return send(res, 200, await login(await readBody(req)), origin);

    const session = verify(String(req.headers.authorization || "").replace(/^Bearer\s+/i, ""));
    if (!session) throw new HttpError(401, "Please log in again.");

    if (route === "tree" && req.method === "GET") {
      const { head, files, collections } = await readTree();
      return send(res, 200, { head, role: session.role, name: session.name, files, collections }, origin);
    }
    if (route === "blob" && req.method === "POST") return send(res, 200, await createBlob(await readBody(req)), origin);
    if (route === "commit" && req.method === "POST") return send(res, 200, await commit(await readBody(req), session), origin);
    if (route === "status" && req.method === "GET") return send(res, 200, await status(url.searchParams.get("sha")), origin);
    throw new HttpError(404, "Not found.");
  } catch (err) {
    const status = err instanceof HttpError ? err.status : 500;
    if (status === 500) console.error(err);
    send(res, status, { error: status === 500 && !(err instanceof HttpError) ? "Server error." : err.message }, origin);
  }
};

// Exposed for tests
module.exports._internal = { photoAllowed, validateCollections, sign, verify };
