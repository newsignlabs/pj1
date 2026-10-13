# Photo admin — setup and use

`/admin/` lets the shop manage photos without GitHub. Changes are saved as one GitHub
commit; the **Build site from photo folders** workflow builds the pictures and Catalyst
Slate publishes the site (about 2–3 minutes).

```
admin page (/admin/, on Slate)  ──login──▶  Catalyst function gallery-api  ──GitHub App──▶  newsignlabs/pj1 (main)
                                                                                              │ workflow builds
                                                                                              ▼
                                                                                    Catalyst Slate publishes
```

| Account | Can do |
|---------|--------|
| **client** | Collections: add / delete photos, choose a card cover, create / rename / delete sub-collections, edit category titles and intros, set prices, show / hide prices |
| **developer** | Everything above, plus add / delete categories and replace the slider, quote, Home category-card, feature, Our Story and logo pictures |

The GitHub key never reaches the browser; the function only accepts image files inside the
photo folders, `content/collections.json` and `content/prices.json`, so the admin cannot change code or pages.

---

## One-time setup (developer)

### 1. Create the GitHub App

GitHub → your profile (or the `newsignlabs` organisation) → **Settings → Developer settings
→ GitHub Apps → New GitHub App**

- **Name:** `cutelook-admin` (any unique name) · **Homepage URL:** the site URL
- **Webhook:** untick **Active**
- **Repository permissions** — set only these:
  - **Contents: Read and write** (read folders, commit photo changes)
  - **Actions: Read-only** (shows "Publishing… / Published" in the admin)
  - Metadata: Read-only (always on)
  - everything else: **No access**
- **Where can this GitHub App be installed?** Only on this account
- **Create**, then on the App page:
  - note the **App ID**
  - **Generate a private key** (downloads a `.pem` file — keep it safe)
  - **Install App** → **Only select repositories** → `pj1` → Install.
    The installation page URL ends in `/installations/<number>`: that number is the
    **Installation ID**.

Repository settings to keep:
- **Settings → Actions → General → Workflow permissions: Read and write** (already set; the
  workflow commits the built pictures).
- If you protect `main` later, add the App to the rule's **bypass list**.

### 2. Choose the two admin passwords

Pick one password for the developer and one for the shop (12+ characters, not used
anywhere else). They are stored as plain text in the function's environment variables
(step 3), so only people with access to the Catalyst project can read them. To change a
password, edit the variable in the Catalyst console; it applies at the next login.

### 3. Create the Catalyst function (in the browser — no laptop or CLI needed)

Everything below works from a phone browser. Use the same Catalyst project that hosts
the Slate site.

**a. Create the function — choose one way**

- **Upload the ready-made ZIP (easiest).** Download
  <https://github.com/newsignlabs/pj1/raw/main/catalyst/gallery-api.zip> to the phone.
  In the **Catalyst console → Serverless → Functions → Create Function**, choose
  **File Upload**, then:
  - Function name: `gallery-api`
  - Type: **Advanced I/O**
  - Stack: **Node.js 18** or newer
  - Upload `gallery-api.zip` and create.
- **Or paste the code.** **Create Function** → name `gallery-api`, type **Advanced I/O**,
  stack **Node.js 18** or newer, **blank template** (not Express). In the function's code
  editor, replace everything in `index.js` with the code from
  <https://raw.githubusercontent.com/newsignlabs/pj1/main/catalyst/functions/gallery-api/index.js>
  (open it, select all, copy, paste) and **Save / Deploy**. No npm packages are needed.

**b. Environment variables** — open **gallery-api → Configuration → Environment
variables** and add:

| Variable | Value |
|----------|-------|
| `GH_APP_ID` | App ID from step 1 |
| `GH_INSTALLATION_ID` | Installation ID from step 1 |
| `GH_PRIVATE_KEY` | the whole `.pem` file, from `-----BEGIN` to `-----END … KEY-----` (see the phone tip below) |
| `GH_OWNER` / `GH_REPO` / `GH_BRANCH` | `newsignlabs` / `pj1` / `main` |
| `DEVELOPER_PASSWORD` | developer password from step 2 (username: `developer`) |
| `CLIENT_PASSWORD` | shop password from step 2 (username: `cutelook`) |
| `DEVELOPER_USERNAME` / `CLIENT_USERNAME` | optional, to use other usernames |
| `SESSION_SECRET` | any long random text, 40+ characters (letters and numbers typed at random are fine); it signs logins |
| `ALLOWED_ORIGINS` | `https://pj1-midrqtyj.onslate.in` (add the custom domain too when it exists, comma-separated) |

Phone tip for `GH_PRIVATE_KEY`: open the downloaded `.pem` file in the phone's Files app
with a text viewer or editor, select all, copy, and paste into the value box. It is fine if
the line breaks turn into spaces or `\n` — the function rebuilds the key.

**c. Copy the function URL** shown on the function's page (it ends in
`/server/gallery-api`). If the admin later shows a CORS / "Failed to fetch" error, add the
site address under **Catalyst console → Settings → Authorized Domains**.

### 4. Connect the admin page (on github.com)

Open `admin/config.js` in the repository on github.com, tap the **pencil (Edit)**, put the
function URL between the quotes, and **Commit changes** to `main`:

```js
window.CUTELOOK_ADMIN = { api: "https://…/server/gallery-api" };
```

After about a minute, open `https://pj1-midrqtyj.onslate.in/admin/` and log in with each
account.

**Updating the function later:** when its code changes in the repository, the ZIP at
`catalyst/gallery-api.zip` is rebuilt automatically; upload it again in the console (or
paste the new `index.js`). On a computer you can instead use the Catalyst CLI from the
`catalyst/` folder (`catalyst deploy --only functions`).

---

## Using the admin (shop)

1. Open **/admin/** and log in.
2. Pick a category (Bridal Sets, Necklaces, …). Each box is a sub-collection — one card on
   the Collections page.
3. **Add photos** (camera roll or files, several at once), **🗑** to delete (tap **↺** to
   undo), **★** to make a photo the card's cover, **Rename** / **Delete** a sub-collection,
   **+ New sub-collection**, or edit the category title and introduction.
4. **Prices:** type the price in rupees (numbers only) in the box under each photo; leave it
   empty for "Price on request". A card shows "From ₹…", its lowest price. The switch
   **Show prices on the website** at the top hides or shows every price; typed prices are
   kept either way.
5. Nothing changes on the website until you press **Save & publish** in the bar at the
   bottom. Photos are shrunk on your phone before uploading, so it is quick on mobile data.
6. Wait for **Published ✓** (2–3 minutes), then refresh the website.

Every save is a GitHub commit, so anything deleted can be restored from the history by the
developer.

Notes:
- A new category (developer) appears on the Collections page; the Home page category cards
  are fixed in `index.html`, so add a card there by hand if wanted.
- If two people save at the same time, the second save is rebuilt on top of the first
  automatically.
