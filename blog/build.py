#!/usr/bin/env python3
"""
D Consulting — blog build.

Reads  blog/posts/*.md   (front-matter + markdown)
Writes blog/index.html, blog/<slug>.html, blog/feed.xml

Front-matter keys:
  title, date (YYYY-MM-DD), lang (en|he), tags (comma separated),
  excerpt, image (optional, path relative to site root), slug (optional)

This is the target the content agent will write into: drop a .md file in
posts/, run this, publish. No CMS, no database.

Requires: pip install markdown
"""
import html
import json
import os
import re
import sys
from datetime import datetime, timezone

try:
    import markdown as md_lib
except ImportError:
    sys.exit("Missing dependency. Run:  pip3 install markdown")

HERE = os.path.dirname(os.path.abspath(__file__))
POSTS_DIR = os.path.join(HERE, "posts")
SITE = "https://dconsult.me"

UI = {
    "en": {
        "back": "← All articles", "home": "← Back to site", "blog": "Insights",
        "kicker": "Insights", "title": "Notes from the front line of hospitality distribution.",
        "sub": "What we're seeing in the market, in the channels, and in the data — written for people who run properties.",
        "empty": "First articles coming shortly.", "read": "Read article",
        "min": "min read", "by": "By",
    },
    "he": {
        "back": "→ כל המאמרים", "home": "→ חזרה לאתר", "blog": "תובנות",
        "kicker": "תובנות", "title": "מהשטח של עולם ההפצה והאירוח.",
        "sub": "מה אנחנו רואים בשוק, בערוצים ובנתונים — נכתב עבור מי שמנהל נכסים בפועל.",
        "empty": "המאמרים הראשונים יעלו בקרוב.", "read": "לקריאת המאמר",
        "min": "דק' קריאה", "by": "מאת",
    },
}


def parse_front_matter(raw):
    """Minimal front-matter parser: --- key: value --- then body."""
    if not raw.startswith("---"):
        return {}, raw
    end = raw.find("\n---", 3)
    if end == -1:
        return {}, raw
    head, body = raw[3:end], raw[end + 4:]
    meta = {}
    for line in head.strip().splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        meta[k.strip()] = v.strip().strip('"').strip("'")
    return meta, body.lstrip("\n")


def slugify(s):
    s = re.sub(r"[^\w\s-]", "", s, flags=re.UNICODE).strip().lower()
    return re.sub(r"[\s_-]+", "-", s) or "post"


def read_posts():
    posts = []
    if not os.path.isdir(POSTS_DIR):
        return posts
    for fn in sorted(os.listdir(POSTS_DIR)):
        if not fn.endswith(".md"):
            continue
        raw = open(os.path.join(POSTS_DIR, fn), encoding="utf-8").read()
        meta, body = parse_front_matter(raw)
        if not meta.get("title"):
            print(f"  ! skipping {fn}: no title")
            continue
        lang = (meta.get("lang") or "en").lower()
        slug = meta.get("slug") or slugify(meta["title"])
        words = len(re.findall(r"\w+", body, flags=re.UNICODE))
        posts.append({
            "file": fn,
            "title": meta["title"],
            "date": meta.get("date", "1970-01-01"),
            "lang": lang if lang in ("en", "he") else "en",
            "tags": [t.strip() for t in (meta.get("tags") or "").split(",") if t.strip()],
            "excerpt": meta.get("excerpt", ""),
            "image": meta.get("image", ""),
            "author": meta.get("author", "Itai Gal"),
            "slug": f"{slug}-{lang}" if lang == "he" else slug,
            "body_html": md_lib.markdown(body, extensions=["extra", "sane_lists"]),
            "minutes": max(1, round(words / 200)),
        })
    posts.sort(key=lambda p: p["date"], reverse=True)
    return posts


def head(title, desc, lang, canonical, image="", back=None):
    rtl = ' dir="rtl"' if lang == "he" else ' dir="ltr"'
    og_img = f"{SITE}/{image}" if image else f"{SITE}/assets/og.png"
    return f"""<!DOCTYPE html>
<html lang="{lang}"{rtl}>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="article">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{og_img}">
<meta name="twitter:card" content="summary_large_image">
<link rel="alternate" type="application/rss+xml" title="D Consulting — Insights" href="{SITE}/blog/feed.xml">
<link rel="icon" type="image/png" href="../assets/icon-512.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;0,700;1,500;1,600&family=Inter:wght@400;500;600;700&family=Heebo:wght@400;500;700;800&family=Frank+Ruhl+Libre:wght@500;700;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../styles.css">
</head>
<body>
<div class="legalbar">
  <div class="container legalbar__inner">
    <a href="../index.html" aria-label="D Consulting home"><img src="../assets/logo-dark.png" alt="D Consulting" style="height:38px;width:auto"></a>
    <a class="back" href="{(back or ('index.html', UI[lang]['back']))[0]}">{html.escape((back or ('index.html', UI[lang]['back']))[1])}</a>
  </div>
</div>
"""


FOOT = """<footer class="footer">
  <div class="container footer__bottom" style="border:0">
    <span>&copy; <span id="year">2026</span> D Consulting.</span>
    <a class="footer__privacy" href="../privacy.html">Privacy</a>
  </div>
</footer>
<script>document.getElementById('year').textContent=new Date().getFullYear();</script>
</body>
</html>
"""


def write(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def build_article(p):
    u = UI[p["lang"]]
    url = f"{SITE}/blog/{p['slug']}.html"
    tags = "".join(f'<span class="ptag">{html.escape(t)}</span>' for t in p["tags"])
    hero = (f'<img class="post__hero" src="../{p["image"]}" alt="">' if p["image"] else "")
    schema = f"""<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"BlogPosting",
"headline":{json.dumps(p['title'], ensure_ascii=False)},
"datePublished":"{p['date']}","inLanguage":"{p['lang']}",
"author":{{"@type":"Person","name":"{html.escape(p['author'])}"}},
"publisher":{{"@type":"Organization","name":"D Consulting","url":"{SITE}"}},
"mainEntityOfPage":"{url}"}}
</script>"""
    return (
        head(f"{p['title']} — D Consulting", p["excerpt"] or p["title"], p["lang"], url, p["image"])
        + f"""<main class="post">
  <div class="post__wrap">
    <p class="post__meta"><time datetime="{p['date']}">{p['date']}</time> · {p['minutes']} {html.escape(u['min'])} · {html.escape(u['by'])} {html.escape(p['author'])}</p>
    <h1 class="post__title">{html.escape(p['title'])}</h1>
    <div class="post__tags">{tags}</div>
    {hero}
    <article class="post__body">
{p['body_html']}
    </article>
    <p class="post__foot"><a class="btn btn--primary" href="../index.html#contact">{'בואו נדבר' if p['lang']=='he' else "Let's talk"}</a></p>
  </div>
</main>
{schema}
"""
        + FOOT
    )


def build_index(posts):
    out = []
    for lang in ("en", "he"):
        u = UI[lang]
        items = [p for p in posts if p["lang"] == lang]
        cards = "".join(
            f"""      <article class="pcard">
        <a class="pcard__link" href="{p['slug']}.html">
          {f'<img class="pcard__img" src="../{p["image"]}" alt="" loading="lazy">' if p['image'] else ''}
          <div class="pcard__body">
            <p class="pcard__meta"><time datetime="{p['date']}">{p['date']}</time> · {p['minutes']} {html.escape(u['min'])}</p>
            <h2 class="pcard__title">{html.escape(p['title'])}</h2>
            <p class="pcard__excerpt">{html.escape(p['excerpt'])}</p>
            <div class="post__tags">{''.join(f'<span class="ptag">{html.escape(t)}</span>' for t in p['tags'])}</div>
          </div>
        </a>
      </article>"""
            for p in items
        ) or f'<p class="pempty">{html.escape(u["empty"])}</p>'
        out.append(f"""  <section class="bloglang" data-lang="{lang}"{'' if lang == 'en' else ' hidden'}>
    <div class="section__head section__head--center">
      <p class="kicker">{html.escape(u['kicker'])}</p>
      <h1 class="h2">{html.escape(u['title'])}</h1>
      <p class="section__sub">{html.escape(u['sub'])}</p>
    </div>
    <div class="pgrid">
{cards}
    </div>
  </section>""")

    body = "\n".join(out)
    return (
        head("Insights — D Consulting", UI["en"]["sub"], "en", f"{SITE}/blog/",
             back=("../index.html", UI["en"]["home"]))
        + f"""<main class="section">
  <div class="container">
{body}
  </div>
</main>
<script>
(function(){{
  var saved='en'; try{{saved=localStorage.getItem('dc_lang')||'en';}}catch(e){{}}
  var qp=new URLSearchParams(location.search).get('lang'); if(qp==='he'||qp==='en') saved=qp;
  function apply(l){{
    document.documentElement.setAttribute('lang',l);
    document.documentElement.setAttribute('dir', l==='he'?'rtl':'ltr');
    [].forEach.call(document.querySelectorAll('.bloglang'),function(s){{
      s.hidden = (s.getAttribute('data-lang')!==l);
    }});
    try{{localStorage.setItem('dc_lang',l);}}catch(e){{}}
  }}
  apply(saved);
}})();
</script>
"""
        + FOOT
    )


def build_feed(posts):
    now = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
    items = "".join(
        f"""    <item>
      <title>{html.escape(p['title'])}</title>
      <link>{SITE}/blog/{p['slug']}.html</link>
      <guid isPermaLink="true">{SITE}/blog/{p['slug']}.html</guid>
      <pubDate>{datetime.strptime(p['date'], '%Y-%m-%d').strftime('%a, %d %b %Y 09:00:00 +0000')}</pubDate>
      <description>{html.escape(p['excerpt'])}</description>
    </item>
"""
        for p in posts
    )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel>
    <title>D Consulting — Insights</title>
    <link>{SITE}/blog/</link>
    <description>Revenue management, distribution and travel-tech insight for hospitality.</description>
    <lastBuildDate>{now}</lastBuildDate>
{items}</channel></rss>
"""


def main():
    posts = read_posts()
    print(f"Found {len(posts)} post(s)")
    for p in posts:
        write(os.path.join(HERE, f"{p['slug']}.html"), build_article(p))
        print(f"  → blog/{p['slug']}.html   [{p['lang']}] {p['title'][:52]}")
    write(os.path.join(HERE, "index.html"), build_index(posts))
    write(os.path.join(HERE, "feed.xml"), build_feed(posts))
    print("  → blog/index.html\n  → blog/feed.xml\nDone.")


if __name__ == "__main__":
    main()
