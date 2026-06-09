# HANDOFF — sabahwebs-exact

Static site for **sabahwebs.com**, hosted on GitHub Pages. Originally a verbatim clone of the
Webflow-served site; now the **live production site** at the custom domain, with custom features
layered on top.
Last updated: 2026-06-09.

---

## 1. What this is

- A self-hosted static site: **homepage (`index.html`) + 10 blog posts** under `/blog/`.
- **It is now the production site:** `sabahwebs.com` DNS points here (GitHub Pages), HTTPS enforced.
  Webflow is no longer in the serving path.
- All CSS, JS, fonts, and images are bundled in the repo, so it renders with **no dependency on
  Webflow's CDN**. Third-party scripts that must stay remote (Google reCAPTCHA, GTM, fonts) load
  from their real `https://` origins.

## 2. Where it lives

| | |
|---|---|
| **GitHub repo** | `fyb27/sabahwebs-exact` (public) |
| **Production URL** | https://sabahwebs.com (custom domain, HTTPS) |
| **Pages URL** | https://fyb27.github.io/sabahwebs-exact/ (still works; canonical is the apex) |
| **Local working dir** | `Z:\sites\sabahwebs happycodes\sabahwebs\mirror` (this folder **is** the git repo root) |
| **Branch** | `main` |

## 3. Custom domain + DNS (live)

- **`CNAME` file** in repo root contains `sabahwebs.com` → tells Pages the canonical custom domain.
- **GoDaddy DNS for sabahwebs.com:**
  - `A  @  185.199.108.153 / .109 / .110 / .111` (the four GitHub Pages IPs)
  - `CNAME  www  fyb27.github.io`
  - Kept: NS, SOA, `_domainconnect`, `TXT @ google-site-verification=…`, `TXT _dmarc …`
  - Removed during cutover: old parking `A @ 198.202.211.1`, the Webflow `CNAME www cdn.webflow.com`, and the stale `TXT _webflow` verification.
- HTTPS: GitHub auto-provisioned the Let's Encrypt cert; **Enforce HTTPS** is on.

## 4. Custom features (on top of the clone)

All wired into the **minified** `index.html` (and floater into all 11 pages). Key knobs:

- **Contact form → Formspree.** Endpoint `https://formspree.io/f/xkoabbdn`. Both forms POST to it:
  the main contact form (`#email-form-2`) and the small footer form (`#email-form`).
  - A capture-phase JS handler (injected before `</body>`) **overrides Webflow's form JS**
    (`stopImmediatePropagation`), submits via `fetch` with `Accept: application/json`, and toggles
    the existing `.w-form-done` / `.w-form-fail` blocks. Field names were cleaned to
    `name` / `email` / `phone` / `message`.
- **Google reCAPTCHA v2** ("I'm not a robot") on the main form.
  - Site key: `6LekYxUtAAAAAMFlBktDLAoKui7TuBk_4tlxoLlA` (registered for `sabahwebs.com` + `www`).
  - Secret key is held by the owner — add it in the **Formspree form settings** for true
    server-side verification (Formspree plan permitting). Without it, the checkbox is a strong
    client-side gate + Formspree anti-spam.
  - `api.js` loads from `https://www.google.com/recaptcha/api.js` (the mirror had stripped the
    protocol → 404; this was fixed). The handler blocks submit until `grecaptcha.getResponse()` is set.
- **WhatsApp** (number `60168430891`):
  - **Floater** `.wa-float` — green circle, bottom-right, on **all 11 pages** (`right:40px` desktop,
    `20px` mobile).
  - **Contact section** has an inline **"WhatsApp us"** button (see §5).
- **Blog tab capped to 3 + "View all" toggle.** Resources → Blog (`data-w-tab="Tab 1"`) shows 3 cards;
  CSS `#blog-limit` hides `:nth-child(n+4)` unless `.blog_grid.show-all` is set; a client-side
  **"View all blogs"** button (built in JS only when >3 posts) toggles `show-all` ⇄ "Show less".
- **Form input font fixed** — single-line contact inputs were `Jetbrainsmono`; switched to the page
  font **`Circe`** in the homepage CSS.

## 5. Contact section structure (homepage)

`<section class="section_contact">` → `.contact_form-component` is now a **single centered column**
(`grid-template-columns:1fr`, max-width ~620px; see inline `#contact-stack-style`). Vertical order:

1. `<h2 class="contact_form-heading">Contact us!</h2>`
2. `<p class="contact_lead">Send us a whatsapp, and we'll be right with you!</p>`
3. **WhatsApp us** button → `wa.me/60168430891` (`.contact_whatsapp-btn`)
4. `<p class="contact_lead contact_lead-or">Or send us an email from the form below!</p>`
5. The email form (`#email-form-2`: name, email, phone, message, reCAPTCHA, Submit) + `.w-form-done`/`.w-form-fail`.

The old two-column layout and right-side image/WhatsApp panel were removed. A header WhatsApp icon was
tried and then **removed** (redundant with the floater).

### Other DOM anchors
- Header nav button: `<a href="#contact-form" class="button is-secondary w-button">Get in touch</a>` inside `.nav-button-wrapper` (blog pages use `../index.html#contact-form`).
- Section IDs used by nav: `#projects`, `#services`, `#resources`, `#faq`, `#contact-form`.
- Services grid: 3 × `.services_grid-item` (`is-design` / `is-seo` / `is-maintenance`).
- Resources tabs: `.resource_tab-link` `data-w-tab="Tab 1|3|4"` (Blog · Webflow · SEO). Only **Tab 1 (Blog)** has a content pane.
- FAQ "How do I get started" answer now leads with WhatsApp + email links.

## 6. Working on this repo

> **The HTML is minified to one line per file.** Don't hand-edit by eye. Locate the target by a
> unique substring and edit with a script (PowerShell `[regex]`/`.Replace` on
> `[IO.File]::ReadAllText`/`WriteAllText` with `UTF8Encoding($false)` — no BOM). Keep `<div>` balanced.
> Injected blocks use stable IDs (`#blog-limit`, `#contact-stack-style`, `#contact-cta-style`,
> `#contact-panel-style`) so edits are idempotent.

### Preview-before-push workflow (standing preference)
The owner reviews changes **locally before any push**. Do not push until approved.
1. Edit files in `mirror`, **don't push**.
2. Serve locally: from the mirror dir run `python -m http.server 8000` (Python and Node both installed)
   → owner opens **http://localhost:8000** (hard-refresh Ctrl+F5).
3. Push only after they say go.

reCAPTCHA + Formspree both work over `http://localhost`, so the preview is high-fidelity.

### Deploy
- **Push to `main` → Pages auto-rebuilds** (~1 min). No build step (`.nojekyll`, served as-is).
- Verify live against `https://sabahwebs.com/...` after the rebuild.
- GitHub auth: account **`fyb27`** via **Git Credential Manager** (no `gh` CLI / `GITHUB_TOKEN`).
  `git push` over HTTPS just works.
- Commit messages: avoid raw `"` quotes (PowerShell here-string passing to `git -m` can split on them).

## 7. Build pipeline (how the original clone was made — for reference)

1. **Mirror** — `wget -H -p -k -E` over the 11 URLs (homepage + 10 blog posts from `sitemap.xml`).
2. **Flatten** — promote `index.html`, `blog/`, badge dir to repo root; strip one leading `../` so
   paths are relative.
3. **Webflow runtime chunks** — `webflow.<hash>.js` lazy-loads 15 `webflow.achunk.<hash>.js` files
   (tabs + IX2 animations); extracted from the loader's `r.u` map and downloaded into `/js/`.
4. **Strip SRI** — removed all `integrity="…"` (wget rewrote `url()` paths in CSS, breaking hashes).

## 8. Known limitations / watch-outs

- **reCAPTCHA secret** not yet confirmed inside Formspree — verify in the Formspree dashboard for true
  server-side token validation.
- **Webflow / SEO resource tabs are empty** — same as the original live site (only Blog has cards).
- Benign console noise: `srcset` descriptor warnings.
- The owner's reCAPTCHA **secret key was shared in chat** once — consider regenerating the key pair and
  swapping the site key if being cautious (low urgency).
