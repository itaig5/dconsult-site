# D Consulting — website

Bilingual (English / Hebrew, with RTL) marketing site for **D Consulting** — a revenue-management, distribution and travel-tech consultancy for hotels and vacation rentals. Plain static HTML/CSS/JS, deployed via **GitHub Pages** at **https://dconsult.me**.

## Local preview
```bash
node serve.js   # → http://localhost:8129
```

## Structure
| File | Purpose |
| --- | --- |
| `index.html` | Single-page site (English content inline + `data-i18n` keys) |
| `privacy.html` | Privacy policy (EN/HE, switched client-side) |
| `styles.css` | Design system — dark hero, light body, brand blue + gold, responsive, RTL |
| `script.js` | EN/HE i18n toggle, mobile nav, scrollspy, contact form |
| `blog/posts/*.md` | The blog's only source. Everything else in `blog/` is generated |
| `blog/build.py` | Generates `blog/*.html`, `blog/feed.xml`, `sitemap.xml`, `llms.txt` — and runs the indexing guards. Run it after editing a post |
| `robots.txt`, `sitemap.xml`, `llms.txt` | Crawler-facing. `sitemap.xml` and `llms.txt` are generated — edit `build.py`, not them |
| `_config.yml` | **Do not delete.** Stops Jekyll publishing the sources: without it, every post is republished at `/blog/posts/*.html` as a duplicate with its own self-referencing canonical, and `README.md`, `serve.js` and `build.py` are served verbatim. Its own header explains why. |
| `.github/workflows/site-checks.yml` | Runs the build on every push, so the indexing guards actually fire and the generated files cannot drift from their sources |
| `assets/og.jpg` | Social-share (Open Graph) image |
| `CNAME` | Custom domain for GitHub Pages |

## Notes
- Language: `?lang=he` forces Hebrew; choice is saved to `localStorage`. It is **not** a separate URL — `/?lang=he` returns byte-identical HTML and canonicalises to `/`, so those URLs must never be declared as `hreflang` alternates. The build fails if they are.
- Contact form posts to **Formspree** if a form ID is set on `#contactForm[data-formspree]`; otherwise it falls back to opening the visitor's email client.
