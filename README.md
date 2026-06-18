# D Consulting — website

Bilingual (English / Hebrew, with RTL) marketing site for **D Consulting** — a revenue-management, distribution and travel-tech consultancy for the hospitality industry. Plain static HTML/CSS/JS, deployed via **GitHub Pages** at **https://dconsult.me**.

## Local preview
```bash
node serve.js   # → http://localhost:8129
```

## Structure
| File | Purpose |
| --- | --- |
| `index.html` | Single-page site (English content inline + `data-i18n` keys) |
| `styles.css` | Design system — dark hero, light body, brand blue + gold, responsive, RTL |
| `script.js` | EN/HE i18n toggle, mobile nav, scrollspy, contact form |
| `assets/og.png` | Social-share (Open Graph) image |
| `CNAME` | Custom domain for GitHub Pages |

## Notes
- Language: `?lang=he` forces Hebrew; choice is saved to `localStorage`.
- Contact form posts to **Formspree** if a form ID is set on `#contactForm[data-formspree]`; otherwise it falls back to opening the visitor's email client.
