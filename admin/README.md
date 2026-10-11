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
| **client** | Collections: add / delete photos, choose a card cover, create / rename / delete sub-collections, edit category titles and intros |
| **developer** | Everything above, plus add / delete categories and replace the slider, quote, Home category-card, feature, Our Story and logo pictures |

The GitHub key never reaches the browser; the function only accepts image files inside the
photo folders and `content/collections.json`, so the admin cannot change code or pages.

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

### 3. Deploy the Catalyst function

Requires the Catalyst CLI (`npm install -g zcatalyst-cli`) and Node 18+.

```bash
cd catalyst
catalyst login
catalyst init          # choose the existing project (the one with the Slate app); keep functions/
catalyst deploy --only functions
```

Then in the **Catalyst console → Serverless → Functions → gallery-api → Configuration →
Environment variables**, add:

| Variable | Value |
|----------|-------|
| `GH_APP_ID` | App ID from step 1 |
| `GH_INSTALLATION_ID` | Installation ID from step 1 |
| `GH_PRIVATE_KEY` | full contents of the `.pem` file (new lines may be written as `\n`) |
| `GH_OWNER` / `GH_REPO` / `GH_BRANCH` | `newsignlabs` / `pj1` / `main` |
| `DEVELOPER_PASSWORD` | developer password from step 2 (username: `developer`) |
| `CLIENT_PASSWORD` | shop password from step 2 (username: `cutelook`) |
| `DEVELOPER_USERNAME` / `CLIENT_USERNAME` | optional, to use other usernames |
| `SESSION_SECRET` | a long random string, e.g. `python3 -c "import secrets;print(secrets.token_urlsafe(48))"` |
| `ALLOWED_ORIGINS` | `https://pj1-midrqtyj.onslate.in` (add the custom domain too when it exists, comma-separated) |

Copy the function's **URL** (ends in `/server/gallery-api`). If the browser reports a CORS
error, also add the site address under **Catalyst console → Settings → Authorized Domains**.

### 4. Connect the admin page

Put the function URL in `admin/config.js`:

```js
window.CUTELOOK_ADMIN = { api: "https://…/server/gallery-api" };
```

Commit to `main`. Open `https://<site>/admin/` and log in with each account.

---

## Using the admin (shop)

1. Open **/admin/** and log in.
2. Pick a category (Bridal Sets, Necklaces, …). Each box is a sub-collection — one card on
   the Collections page.
3. **Add photos** (camera roll or files, several at once), **🗑** to delete (tap **↺** to
   undo), **★** to make a photo the card's cover, **Rename** / **Delete** a sub-collection,
   **+ New sub-collection**, or edit the category title and introduction.
4. Nothing changes on the website until you press **Save & publish** in the bar at the
   bottom. Photos are shrunk on your phone before uploading, so it is quick on mobile data.
5. Wait for **Published ✓** (2–3 minutes), then refresh the website.

Every save is a GitHub commit, so anything deleted can be restored from the history by the
developer.

Notes:
- A new category (developer) appears on the Collections page; the Home page category cards
  are fixed in `index.html`, so add a card there by hand if wanted.
- If two people save at the same time, the second save is rebuilt on top of the first
  automatically.
