# HANDOFF — sabahwebs-exact

A self-contained static **clone of the live sabahwebs.com site**, hosted on GitHub Pages.
Last updated: 2026-06-09.

---

## 1. What this is

- An exact, self-hosted mirror of **https://sabahwebs.com/** (homepage + 10 blog posts).
- The live apex `sabahwebs.com` is **still served by Webflow** — the DNS cutover to GitHub Pages never happened. This repo is an independent copy, not the production site.
- All CSS, JS, fonts, and images are downloaded into the repo, so the site renders with **no dependency on Webflow's CDN**.

## 2. Where it lives

| | |
|---|---|
| **GitHub repo** | `fyb27/sabahwebs-exact` (public) |
| **Live URL** | https://fyb27.github.io/sabahwebs-exact/ |
| **Local working dir** | `Z:\sites\sabahwebs happycodes\sabahwebs\mirror` (this folder **is** the git repo root) |
| **Branch** | `main` |
| **Size** | ~21 MB, ~160 tracked files |

## 3. Layout

```
/index.html                         homepage (Webflow HTML, minified — single long line)
/blog/<slug>.html                   10 blog posts (served at /blog/<slug> by Pages)
/cdn.prod.website-files.com/...      self-hosted Webflow CSS/JS/fonts/images + chunks
/d3e54v103j8qbb.cloudfront.net/...   jQuery
/ajax.googleapis.com/...            Webfont loader
/www.google.com, /www.googletagmanager.com, /analytics.ahrefs.com   3rd-party stubs
/g0lnomhfn3.../...                   Webflow badge asset
/.nojekyll                          tells Pages to serve files verbatim (filenames have spaces)
/README.md, /HANDOFF.md
```

> **Note:** the HTML is **minified to one line per file**. Don't try to hand-edit by eye —
> use a script that locates the target by a unique substring or by depth-scanning `<div>`/`</div>`.

## 4. How it was built (reproducible pipeline)

1. **Mirror** — `wget -H -p -k -E` over the 11 URLs (homepage + 10 blog posts from sitemap.xml).
2. **Flatten** — promote `index.html`, `blog/`, and the Webflow-badge dir out of the `sabahwebs.com/` host folder up to repo root; strip one leading `../` from references to external host dirs so paths are **relative** (work at the Pages project subpath).
3. **Self-host gaps** — download the apple-touch-icon (`favicon webclip.png`) that wget dropped.
4. **Webflow runtime chunks** — `webflow.<hash>.js` is a tiny webpack loader that lazy-loads `webflow.achunk.<hash>.js` files (the tabs engine + IX2 animations); wget can't follow JS imports, so all 15 chunks were extracted from the loader's `r.u` map and downloaded into the same `/js/` dir.
5. **Strip SRI** — remove all `integrity="…"` attributes (wget rewrote `url()` paths inside the CSS, breaking the hashes → browsers blocked the stylesheet).

## 5. Customizations made on top of the exact clone

In commit order (newest first):

| Commit | Change |
|---|---|
| `d2376ec` | **Removed the E-Commerce tab** from the Resources section (tabs now Blog · Webflow · SEO). |
| `f12cfd0` | Rewrote the 3 service cards with client copy; added a **wrench+gear** maintenance icon (`/cdn.prod.website-files.com/6562ebb5332c7603e8b85f32/wrench-gear.svg`, color `#AEDEFF`). |
| `59a8921` | **Trimmed Services from 6 cards to 3** (Web Design · SEO Optimization · Website Maintenance); removed Web Development, E-Commerce, Site Migration, Content Writing. |
| `1734d8b` | **Repointed header nav** from `https://www.sabahwebs.com/#section` to local targets: homepage uses `#section`; blog pages use `../index.html#section`; logo → `index.html`. SEO meta tags left absolute. |
| `174dab9` | Removed SRI integrity attributes (see step 5). |
| `64f62c4` | Added Webflow runtime chunks (see step 4). |
| `5d0a18b` | Initial exact static clone. |

### Key DOM anchors (homepage `index.html`)
- Services grid: `<div class="services_grid">` … 3 × `.services_grid-item` (node IDs `_74aa9d56` / `e3126f29` / `_38f2a5ba`; accents `is-design` / `is-seo` / `is-maintenance`). Desktop grid is 3 columns, auto-flow.
- Resources tabs: `.resource_tab-link` with `data-w-tab="Tab 1|3|4"` (Tab 2 was E-Commerce, now deleted). **Only Tab 1 (Blog) has a content pane**; Webflow/SEO tabs were empty on the original site too.
- Homepage section IDs used by nav: `#projects`, `#services`, `#resources`, `#faq`, `#contact-form`.

## 6. Deploy / workflow

- **Push to `main` → GitHub Pages auto-rebuilds** (~1–2 min). No build step; static files served as-is (`.nojekyll`).
- Verify live with `curl` against `https://fyb27.github.io/sabahwebs-exact/...` after a rebuild.
- For visual checks, the `seo-visual` agent (headless Playwright) was used; its `screenshots/` and `scripts/` scratch dirs are **gitignored** — delete them from disk after use.
- GitHub auth on this machine: account **`fyb27`** via **Git Credential Manager** (no `gh` CLI, no `GITHUB_TOKEN` env). `git push` over HTTPS just works. For REST API (create repo, enable Pages), pull the token from GCM in PowerShell.

## 7. Known limitations / not done

- **Contact form returns HTTP 405** — a Webflow form needs Webflow's backend to process submissions; a static host can't. Wire it to a service like Formspree if a working form is needed.
- **`<link rel="canonical">` is relative** (`index.html`) — wget's link-converter did this. Harmless for the clone; set to an absolute URL if this is ever made canonical.
- **Webflow / SEO resource tabs are empty** — same as the original live site (only the Blog tab has cards).
- Benign console noise: `srcset` descriptor warnings, and 405s on the form/analytics endpoints.
- Still on the `github.io` URL — **no custom domain** attached (by request).

## 8. Common next tasks

- Attach a custom domain (add domain in Pages settings + `CNAME` file + DNS A records `185.199.108–111.153`).
- Make the contact form work (Formspree).
- Edit content: locate the target by unique substring in the minified HTML; keep `<div>`/`</div>` balanced; push and re-verify live.
